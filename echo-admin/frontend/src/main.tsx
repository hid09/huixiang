import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App.tsx';
import './styles/global.less';

// Ant Design 主题配置
const theme = {
  token: {
    colorPrimary: '#4ecdc4',
    colorSuccess: '#4ecdc4',
    colorWarning: '#feca57',
    colorError: '#ff6b6b',
    borderRadius: 8,
    fontSize: 14,
  },
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ConfigProvider theme={theme} locale={zhCN}>
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </StrictMode>
);
