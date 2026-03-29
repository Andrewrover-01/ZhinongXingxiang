/**
 * camera.ts
 *
 * Abstraction layer for camera / image-picker functionality.
 *
 * - In a Capacitor native app (Android/iOS):  uses @capacitor/camera for full
 *   access to the device camera and photo library.
 * - In a browser / PWA:  falls back to a hidden <input type="file"> element so
 *   the existing web behaviour is preserved with zero changes to callers.
 */

import { Capacitor } from "@capacitor/core";

// Lazy-import the Camera plugin only in native environments to avoid pulling in
// Capacitor's native bridge in the browser bundle.
async function getCameraPlugin() {
  const { Camera, CameraResultType, CameraSource } = await import(
    "@capacitor/camera"
  );
  return { Camera, CameraResultType, CameraSource };
}

export type CaptureResult = {
  /** A data-URL or object-URL suitable for use in <img src="…"> */
  previewUrl: string;
  /** A Blob ready to be uploaded via FormData */
  blob: Blob;
};

/**
 * Opens the native camera (Capacitor) or triggers a file-input dialog
 * (browser / PWA).
 *
 * @param source  "camera" | "gallery" — ignored in browsers (always shows the
 *                file picker which lets users choose either on mobile).
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

    // Convert data-URL → Blob for FormData upload
    const blob = dataUrlToBlob(image.dataUrl);
    return { previewUrl: image.dataUrl, blob };
  } catch (err) {
    // User cancelled or permission denied — not a hard error
    const msg = err instanceof Error ? err.message : String(err);
    if (!msg.toLowerCase().includes("cancel")) {
      console.error("[camera] captureNative error:", err);
    }
    return null;
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
