/**
 * camera.ts
 *
 * Abstraction layer for camera / image-picker functionality.
 *
 * - In a Capacitor native app (Android/iOS):  uses @capacitor/camera for full
 *   access to the device camera and photo library, with explicit permission
 *   checking and @capacitor/filesystem-based local image caching.
 * - In a browser / PWA:  falls back to a hidden <input type="file"> element so
 *   the existing web behaviour is preserved with zero changes to callers.
 */

import { Capacitor } from "@capacitor/core";

// Lazy-import the Camera plugin only in native environments to avoid pulling in
// Capacitor's native bridge in the browser bundle.
async function getCameraPlugin() {
  const { Camera, CameraResultType, CameraSource } =
    await import("@capacitor/camera");
  return { Camera, CameraResultType, CameraSource };
}

async function getFilesystemPlugin() {
  const { Filesystem, Directory, Encoding } = await import(
    "@capacitor/filesystem"
  );
  return { Filesystem, Directory, Encoding };
}

export type CaptureResult = {
  /** A data-URL or object-URL suitable for use in <img src="…"> */
  previewUrl: string;
  /** A Blob ready to be uploaded via FormData */
  blob: Blob;
  /** Path to the locally cached copy (native only, undefined in browser) */
  cachedPath?: string;
};

export type PermissionStatus = "granted" | "denied" | "prompt" | "unknown";

/**
 * Checks current camera + photos permission status.
 * Returns "unknown" on non-native platforms.
 */
export async function checkCameraPermissions(): Promise<PermissionStatus> {
  if (!Capacitor.isNativePlatform()) return "unknown";
  try {
    const { Camera } = await getCameraPlugin();
    const status = await Camera.checkPermissions();
    const camState = status.camera;
    if (camState === "granted") return "granted";
    if (camState === "denied") return "denied";
    return "prompt";
  } catch {
    return "unknown";
  }
}

/**
 * Requests camera + photos permissions.
 * Returns the resulting status.
 */
export async function requestCameraPermissions(): Promise<PermissionStatus> {
  if (!Capacitor.isNativePlatform()) return "unknown";
  try {
    const { Camera } = await getCameraPlugin();
    const status = await Camera.requestPermissions({
      permissions: ["camera", "photos"],
    });
    const camState = status.camera;
    if (camState === "granted") return "granted";
    if (camState === "denied") return "denied";
    return "prompt";
  } catch {
    return "denied";
  }
}

/**
 * Opens the native camera (Capacitor) or triggers a file-input dialog
 * (browser / PWA).
 *
 * On native: checks / requests permissions first, caches the image locally
 * via Filesystem, then returns the result.
 *
 * @param source  "camera" | "gallery" — ignored in browsers.
 */
export async function captureImage(
  source: "camera" | "gallery" = "camera"
): Promise<CaptureResult | null> {
  if (Capacitor.isNativePlatform()) {
    return captureNative(source);
  }
  // Browser fallback is triggered by the caller via fileRef.current?.click()
  // This function returning null signals the caller to use the file input.
  return null;
}

/** Use the Capacitor Camera plugin on Android / iOS */
async function captureNative(
  source: "camera" | "gallery"
): Promise<CaptureResult | null> {
  try {
    // Ensure permissions are granted before opening the camera / gallery
    const permStatus = await checkCameraPermissions();
    if (permStatus === "denied") {
      console.warn("[camera] Camera permission denied.");
      return null;
    }
    if (permStatus === "prompt") {
      const granted = await requestCameraPermissions();
      if (granted !== "granted") return null;
    }

    const { Camera, CameraResultType, CameraSource } = await getCameraPlugin();
    const image = await Camera.getPhoto({
      quality: 85,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source:
        source === "camera" ? CameraSource.Camera : CameraSource.Photos,
      saveToGallery: false,
      correctOrientation: true,
    });

    if (!image.dataUrl) return null;

    const blob = dataUrlToBlob(image.dataUrl);

    // Cache the image locally so it is available offline / for re-uploads
    const cachedPath = await cacheImageLocally(image.dataUrl);

    return { previewUrl: image.dataUrl, blob, cachedPath };
  } catch (err) {
    // User cancelled or permission denied — not a hard error
    const msg = err instanceof Error ? err.message : String(err);
    if (!msg.toLowerCase().includes("cancel")) {
      console.error("[camera] captureNative error:", err);
    }
    return null;
  }
}

/**
 * Saves a data-URL image to the app's cache directory via @capacitor/filesystem.
 * Returns the file path on success, undefined on failure.
 */
async function cacheImageLocally(dataUrl: string): Promise<string | undefined> {
  try {
    const { Filesystem, Directory } = await getFilesystemPlugin();
    const filename = `capture_${Date.now()}.jpg`;
    const base64Data = dataUrl.split(",")[1];
    await Filesystem.writeFile({
      path: `zhinong_cache/${filename}`,
      data: base64Data,
      directory: Directory.Cache,
      recursive: true,
    });
    return `zhinong_cache/${filename}`;
  } catch (err) {
    // Caching is best-effort; don't block the user flow
    console.warn("[camera] Failed to cache image locally:", err);
    return undefined;
  }
}

/** Convert a base64 data-URL to a Blob */
function dataUrlToBlob(dataUrl: string): Blob {
  const [header, base64] = dataUrl.split(",");
  const mime = header.match(/:(.*?);/)?.[1] ?? "image/jpeg";
  const binary = atob(base64);
  const array = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    array[i] = binary.charCodeAt(i);
  }
  return new Blob([array], { type: mime });
}

/** Returns true when the code is running inside the Capacitor native shell */
export function isNative(): boolean {
  return Capacitor.isNativePlatform();
}
