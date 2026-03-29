"use client";

import { useEffect } from "react";
import { initPushNotifications } from "@/lib/notifications";

/**
 * CapacitorInit — mounts once at app startup.
 *
 * Handles all Capacitor-specific initialisation that must run on the client:
 * - Push notification registration (native only)
 *
 * Renders nothing visible.
 */
export function CapacitorInit() {
  useEffect(() => {
    // Initialise push notifications (no-op in browser / PWA)
    initPushNotifications();
  }, []);

  return null;
}
