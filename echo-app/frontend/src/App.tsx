/**
 * 回响 - 主应用组件
 */
import { BrowserRouter, Routes, Route, Outlet, useLocation } from 'react-router-dom'
import Home from '@/pages/Home/Home'
import Record from '@/pages/Record/Record'
import RecordDetail from '@/pages/RecordDetail/RecordDetail'
import DiaryList from '@/pages/DiaryList/DiaryList'
import DiaryDetail from '@/pages/DiaryDetail/DiaryDetail'
import Growth from '@/pages/Growth/Growth'
import Profile from '@/pages/Profile/Profile'
import Login from '@/pages/Login/Login'
import Register from '@/pages/Register/Register'
import TabBar from '@/components/TabBar/TabBar'
import PrivateRoute from '@/components/PrivateRoute/PrivateRoute'
import '@/styles/design-tokens.css'

// 带TabBar的布局
function TabLayout() {
  const location = useLocation()
  const showTabBar = !location.pathname.startsWith('/record')

  return (
    <div className="app-container">
      <main className={showTabBar ? 'with-tabbar' : ''}>
        <Outlet />
      </main>
      {showTabBar && <TabBar />}
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 受保护路由 */}
        <Route element={<PrivateRoute><TabLayout /></PrivateRoute>}>
          <Route path="/" element={<Home />} />
          <Route path="/record/:id" element={<RecordDetail />} />
          <Route path="/diary" element={<DiaryList />} />
          <Route path="/diary/:date" element={<DiaryDetail />} />
          <Route path="/growth" element={<Growth />} />
          <Route path="/profile" element={<Profile />} />
        </Route>

        <Route path="/record" element={<PrivateRoute><Record /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
