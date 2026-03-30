import { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.zhinong.xingxiang",
  appName: "智农兴乡",
  webDir: "out",
  // When running in native app, load from the bundled web assets.
  // Set SERVER_URL env var at build time to point to a live backend during
  // development / live-reload: CAPACITOR_SERVER_URL=http://192.168.x.x:3000
  server: process.env.CAPACITOR_SERVER_URL
    ? {
        url: process.env.CAPACITOR_SERVER_URL,
        cleartext: true,
      }
    : undefined,
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: "#ffffff",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true,
    },
    StatusBar: {
      style: "Default",
      backgroundColor: "#16a34a",
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
    },
    Camera: {
      // Allow users to choose between camera and gallery on Android
    },
  },
  android: {
    // Allow localhost cleartext (for dev server live-reload only)
    allowMixedContent: true,
    // Use the system font
    flavor: "main",
  },
};

export default config;
