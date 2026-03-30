/**
 * notifications.ts
 *
 * Push notification integration via @capacitor/push-notifications.
 *
 * Usage: call `initPushNotifications()` once at app startup (e.g. in the root
 * layout) when running inside the Capacitor native shell.
 *
 * On Android the system automatically creates a default notification channel.
 * On iOS the user is prompted to grant notification permission.
 */

import { Capacitor } from "@capacitor/core";

async function getPushPlugin() {
  const { PushNotifications } = await import("@capacitor/push-notifications");
  return { PushNotifications };
}

/**
 * Initialises push notifications for the native app.
 * - Requests permission (Android 13+ / iOS requires this)
 * - Registers with the platform push service (FCM / APNs)
 * - Attaches listeners for registration, errors and incoming messages
 *
 * Safe to call on non-native platforms — returns immediately.
 */
export async function initPushNotifications(): Promise<void> {
  if (!Capacitor.isNativePlatform()) return;

  try {
    const { PushNotifications } = await getPushPlugin();

    // 1. Check existing permission state
    let permStatus = await PushNotifications.checkPermissions();

    // 2. Request permission if needed
    if (permStatus.receive === "prompt") {
      permStatus = await PushNotifications.requestPermissions();
    }

    if (permStatus.receive !== "granted") {
      console.warn("[notifications] Push notification permission not granted.");
      return;
    }

    // 3. Register with the push service
    await PushNotifications.register();

    // 4. Attach event listeners (idempotent — safe to call multiple times)
    await PushNotifications.addListener("registration", (token) => {
      console.info("[notifications] Device registered. Token:", token.value);
      // TODO: send token.value to the backend for server-side push delivery
    });

    await PushNotifications.addListener("registrationError", (err) => {
      console.error("[notifications] Registration error:", err.error);
    });

    await PushNotifications.addListener(
      "pushNotificationReceived",
      (notification) => {
        // Notification received while app is in foreground
        console.info("[notifications] Received:", notification.title);
      }
    );

    await PushNotifications.addListener(
      "pushNotificationActionPerformed",
      (action) => {
        // User tapped the notification
        console.info(
          "[notifications] Action performed:",
          action.actionId,
          action.notification.data
        );
      }
    );
  } catch (err) {
    // Non-fatal — app works without push notifications
    console.warn("[notifications] initPushNotifications failed:", err);
  }
}

/**
 * Removes all push notification listeners and unregisters.
 * Call during app teardown if needed.
 */
export async function teardownPushNotifications(): Promise<void> {
  if (!Capacitor.isNativePlatform()) return;
  try {
    const { PushNotifications } = await getPushPlugin();
    await PushNotifications.removeAllListeners();
  } catch {
    // ignore
  }
}
