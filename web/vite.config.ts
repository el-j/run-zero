import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:49505",
        changeOrigin: true,
      },
    },
  },
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    
  },
});
