import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// Vite config — port 3000, allow all hosts (preview URL proxies through)
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
      allowedHosts: true,
      hmr: {
        clientPort: 443,
        protocol: 'wss',
      },
    },
    preview: {
      host: '0.0.0.0',
      port: 3000,
    },
    define: {
      'process.env.REACT_APP_BACKEND_URL': JSON.stringify(env.REACT_APP_BACKEND_URL || ''),
    },
  };
});
