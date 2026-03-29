"""
locustfile.py — 《智农兴乡》API 性能压测脚本
================================================

目标（源自 PLAN.md §4.4）：
  · 100 并发用户
  · API 响应时间 P95 ≤ 5 秒
  · 错误率 ≤ 1%

覆盖的用户场景
──────────────
  ZhinongReadUser   — 只读型访客（列表、搜索、健康检查）
  ZhinongFarmUser   — 农田管理用户（创建 / 列表 / 更新 / 删除农田）
  ZhinongAIUser     — AI 医生用户（提交诊断、查看历史）
  ZhinongPolicyUser — 农策助手用户（发起政策问答会话）
  ZhinongMixUser    — 混合型用户（模拟典型日活用户行为）

运行方式
──────────
  # Web UI 方式（开发/调试）
  locust -f locustfile.py --host http://localhost:8000

  # 无头方式（CI/CD）
  locust -f locustfile.py --host http://localhost:8000 \
         --users 100 --spawn-rate 10 --run-time 120s --headless \
         --csv load_test_results

  # 使用 locust.conf 默认配置
  locust -f locustfile.py
"""

from __future__ import annotations

import random
import string
import uuid
from typing import Optional

from locust import HttpUser, TaskSet, between, task, events


# ── Helpers ────────────────────────────────────────────────────────────────────

def _random_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def _register_and_login(client) -> Optional[str]:
    """
    Register a unique user, then log in and return the Bearer token.
    Returns None if either request fails (the caller skips the scenario).
    """
    suffix = _random_suffix(8)
    username = f"lt_{suffix}"
    phone = f"1{''.join(random.choices(string.digits, k=10))}"[:11]
    password = "Locust@123"

    reg = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "phone": phone,
            "password": password,
            "real_name": "压测用户",
            "province": "测试省",
            "city": "测试市",
        },
        name="/api/v1/auth/register",
        catch_response=True,
    )
    if reg.status_code not in (200, 201):
        reg.failure(f"Register failed: {reg.status_code} {reg.text[:120]}")
        return None
    reg.success()

    login = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
        name="/api/v1/auth/login",
        catch_response=True,
    )
    if login.status_code != 200:
        login.failure(f"Login failed: {login.status_code} {login.text[:120]}")
        return None
    login.success()
    return login.json().get("access_token")


# ── Task sets ──────────────────────────────────────────────────────────────────

class ReadTasks(TaskSet):
    """
    Read-only tasks: health check, knowledge list, knowledge search.
    Weight reflects typical read-heavy traffic patterns.
    """

    @task(5)
    def health_check(self):
        with self.client.get("/health", name="/health", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"Health check failed: {r.status_code}")

    @task(3)
    def list_knowledge(self):
        params = {"skip": 0, "limit": 20}
        with self.client.get(
            "/api/v1/knowledge/",
            params=params,
            name="/api/v1/knowledge/ [list]",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 401, 403):
                r.success()
            else:
                r.failure(f"list_knowledge: {r.status_code}")

    @task(4)
    def search_knowledge(self):
        queries = ["水稻病虫害", "小麦白粉病", "补贴政策", "合理密植", "玉米螟防治"]
        q = random.choice(queries)
        with self.client.get(
            "/api/v1/knowledge/search",
            params={"q": q, "limit": 5},
            name="/api/v1/knowledge/search",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 401, 403):
                r.success()
            else:
                r.failure(f"search_knowledge: {r.status_code}")

    @task(2)
    def api_root(self):
        with self.client.get("/", name="/", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"root: {r.status_code}")


class FarmlandTasks(TaskSet):
    """CRUD operations on farmlands (requires auth)."""

    _token: Optional[str] = None
    _farmland_ids: list = []

    def on_start(self):
        self._token = _register_and_login(self.client)
        self._farmland_ids = []

    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"} if self._token else {}

    @task(3)
    def list_farmlands(self):
        if not self._token:
            return
        with self.client.get(
            "/api/v1/farmlands/",
            headers=self._auth(),
            name="/api/v1/farmlands/ [list]",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"list_farmlands: {r.status_code}")

    @task(2)
    def create_farmland(self):
        if not self._token:
            return
        payload = {
            "name": f"压测农田_{_random_suffix(4)}",
            "location": "测试省测试市",
            "area": round(random.uniform(0.5, 50.0), 2),
            "crop_type": random.choice(["水稻", "小麦", "玉米", "大豆"]),
        }
        with self.client.post(
            "/api/v1/farmlands/",
            json=payload,
            headers=self._auth(),
            name="/api/v1/farmlands/ [create]",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 201):
                fid = r.json().get("id")
                if fid:
                    self._farmland_ids.append(fid)
                r.success()
            else:
                r.failure(f"create_farmland: {r.status_code} {r.text[:80]}")

    @task(1)
    def update_farmland(self):
        if not self._token or not self._farmland_ids:
            return
        fid = random.choice(self._farmland_ids)
        with self.client.put(
            f"/api/v1/farmlands/{fid}",
            json={"crop_type": random.choice(["水稻", "小麦", "油菜"])},
            headers=self._auth(),
            name="/api/v1/farmlands/{id} [update]",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"update_farmland: {r.status_code}")

    @task(1)
    def delete_farmland(self):
        if not self._token or not self._farmland_ids:
            return
        fid = self._farmland_ids.pop()
        with self.client.delete(
            f"/api/v1/farmlands/{fid}",
            headers=self._auth(),
            name="/api/v1/farmlands/{id} [delete]",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 204, 404):
                r.success()
            else:
                r.failure(f"delete_farmland: {r.status_code}")


class AIDoctorTasks(TaskSet):
    """AI Doctor diagnosis tasks (requires auth)."""

    _token: Optional[str] = None
    _record_ids: list = []

    def on_start(self):
        self._token = _register_and_login(self.client)
        self._record_ids = []

    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"} if self._token else {}

    @task(3)
    def diagnose(self):
        if not self._token:
            return
        symptoms = [
            "叶片出现褐色斑点，边缘枯黄",
            "茎基部出现水渍状病斑，植株萎蔫",
            "叶片背面有白色粉末状物",
            "幼苗茎基部缢缩，猝倒死亡",
            "穗部出现粉红色霉层",
        ]
        crops = ["水稻", "小麦", "玉米", "大豆", "蔬菜"]
        payload = {
            "image_url": f"https://example.com/test_{_random_suffix(6)}.jpg",
            "description": random.choice(symptoms),
            "crop_type": random.choice(crops),
        }
        with self.client.post(
            "/api/v1/ai-doctor/diagnose",
            json=payload,
            headers=self._auth(),
            name="/api/v1/ai-doctor/diagnose",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 201):
                rid = r.json().get("record_id")
                if rid:
                    self._record_ids.append(rid)
                r.success()
            else:
                r.failure(f"diagnose: {r.status_code} {r.text[:80]}")

    @task(2)
    def list_records(self):
        if not self._token:
            return
        with self.client.get(
            "/api/v1/ai-doctor/records",
            headers=self._auth(),
            name="/api/v1/ai-doctor/records [list]",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"list_records: {r.status_code}")

    @task(1)
    def get_record(self):
        if not self._token or not self._record_ids:
            return
        rid = random.choice(self._record_ids)
        with self.client.get(
            f"/api/v1/ai-doctor/records/{rid}",
            headers=self._auth(),
            name="/api/v1/ai-doctor/records/{id}",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"get_record: {r.status_code}")


class PolicyTasks(TaskSet):
    """Policy assistant chat tasks (requires auth)."""

    _token: Optional[str] = None
    _session_id: Optional[str] = None

    def on_start(self):
        self._token = _register_and_login(self.client)
        self._session_id = str(uuid.uuid4())

    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self._token}"} if self._token else {}

    @task(4)
    def policy_chat(self):
        if not self._token:
            return
        questions = [
            "种粮补贴怎么申请？",
            "农业保险有哪些种类？",
            "土地流转需要什么手续？",
            "化肥补贴政策是什么？",
            "农机购置补贴如何领取？",
        ]
        payload = {
            "session_id": self._session_id,
            "message": random.choice(questions),
        }
        with self.client.post(
            "/api/v1/policy/chat",
            json=payload,
            headers=self._auth(),
            name="/api/v1/policy/chat",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"policy_chat: {r.status_code} {r.text[:80]}")

    @task(2)
    def list_sessions(self):
        if not self._token:
            return
        with self.client.get(
            "/api/v1/policy/sessions",
            headers=self._auth(),
            name="/api/v1/policy/sessions [list]",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"list_sessions: {r.status_code}")

    @task(1)
    def get_session(self):
        if not self._token or not self._session_id:
            return
        with self.client.get(
            f"/api/v1/policy/sessions/{self._session_id}",
            headers=self._auth(),
            name="/api/v1/policy/sessions/{id}",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"get_session: {r.status_code}")


# ── User types ─────────────────────────────────────────────────────────────────

class ZhinongReadUser(HttpUser):
    """
    匿名/只读用户 — 浏览知识库和健康检查。
    占比高，等待时间短，模拟高频低权限流量。
    """
    tasks = [ReadTasks]
    wait_time = between(0.5, 2)
    weight = 3


class ZhinongFarmUser(HttpUser):
    """
    农田管理用户 — 登录后管理农田信息。
    """
    tasks = [FarmlandTasks]
    wait_time = between(1, 4)
    weight = 2


class ZhinongAIUser(HttpUser):
    """
    AI 医生用户 — 提交病害诊断请求，最耗时，占比较低。
    wait_time 宽松以贴近真实用户拍照上传的节奏。
    """
    tasks = [AIDoctorTasks]
    wait_time = between(3, 8)
    weight = 2


class ZhinongPolicyUser(HttpUser):
    """
    农策助手用户 — 政策问答，中等频率。
    """
    tasks = [PolicyTasks]
    wait_time = between(2, 6)
    weight = 2


class ZhinongMixUser(HttpUser):
    """
    混合型用户 — 模拟日常活跃用户，随机访问各功能模块。
    """
    tasks = {
        ReadTasks: 4,
        FarmlandTasks: 2,
        AIDoctorTasks: 2,
        PolicyTasks: 2,
    }
    wait_time = between(1, 5)
    weight = 1


# ── Custom metrics hook ────────────────────────────────────────────────────────

@events.quitting.add_listener
def _check_acceptance_criteria(environment, **kwargs):
    """
    验收标准检查（对应 PLAN.md §4.4）：
      · P95 响应时间 ≤ 5000 ms
      · 错误率 ≤ 1%
    如不达标则以退出码 1 退出，方便 CI 门控。
    """
    stats = environment.runner.stats
    total = stats.total
    if total.num_requests == 0:
        return

    p95_ms = total.get_response_time_percentile(0.95)
    error_rate = total.num_failures / total.num_requests

    print("\n" + "=" * 60)
    print("【压测验收报告】")
    print(f"  总请求数  : {total.num_requests}")
    print(f"  失败请求数: {total.num_failures}")
    print(f"  错误率    : {error_rate * 100:.2f}%  (目标 ≤ 1%)")
    print(f"  P95 响应  : {p95_ms:.0f} ms  (目标 ≤ 5000 ms)")
    print("=" * 60)

    passed = True
    if p95_ms is not None and p95_ms > 5000:
        print(f"  ✗ P95 ({p95_ms:.0f} ms) 超出 5000 ms 目标")
        passed = False
    if error_rate > 0.01:
        print(f"  ✗ 错误率 ({error_rate * 100:.2f}%) 超出 1% 目标")
        passed = False
    if passed:
        print("  ✓ 所有验收指标达标")
    print("=" * 60 + "\n")

    if not passed:
        environment.process_exit_code = 1
