import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React 相关
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // UI 组件
          'ui-vendor': ['antd'],
          // 图表库
          'charts-vendor': ['echarts-for-react', 'echarts'],
          // 工具库
          'utils-vendor': ['dayjs', 'axios'],
        },
      },
    },
    chunkSizeWarningLimit: 800,
  },
});
