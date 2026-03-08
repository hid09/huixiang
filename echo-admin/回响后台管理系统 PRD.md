# 回响后台管理系统 PRD

## 1. 项目概述

### 1.1 项目背景
回响项目已上线运行，需要一个独立的后台管理系统，方便管理员查看用户数据、录音记录和生成的日记，评估AI日记生成效果。

### 1.2 技术栈
- **前端**：React 18 + Ant Design Pro 6.x
- **后端**：FastAPI + SQLAlchemy 2.x
- **数据库**：MySQL（与回响共享，只读账号）
- **部署**：同服务器 + Supervisor + Nginx

### 1.3 核心功能

| 模块 | 功能 | 权限 |
|-----|------|------|
| **登录** | 账号密码登录 | 无 |
| **用户管理** | 查看用户列表、 查看用户详情 + 查看录音记录 | 超管/普通 |
| **日记管理** | 查看日记列表 | 查看日记详情（录音→日记对比） | 超管/普通 |
| **系统设置** | 管理后台账号 | 超管 |

## 2. 数据库设计

### 2.1 只读数据表（来自回响项目）

#### users 表
```sql
SELECT id, username, phone, created_at FROM users;
```

#### records 表
```sql
SELECT
    id, user_id, content, created_at,
    emotion_type, emotion_score, asr_emotion, mood_tag, input_type, local_date
FROM records;
```

#### diaries 表
```sql
SELECT
    id, user_id, diary_date, emotion_type, mood_tag,
    what_happened, thoughts, small_discovery, keywords, cognitive_change
FROM diaries;
```

### 2.2 自有数据表

#### admin_users 表
```sql
CREATE TABLE admin_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('super', 'viewer') DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. API 设计

### 3.1 登录模块

| 接口 | 方法 | 说明 |
|-----|------|------|
| /api/admin/login | POST | 管理员登录 |
| /api/admin/logout | POST | 退出登录 |
| /api/admin/me | GET | 获取当前用户信息 |

### 3.2 用户管理

| 接口 | 方法 | 说明 |
|-----|------|------|
| /api/admin/users | GET | 获取用户列表（分页/搜索） |
| /api/admin/users/{id} | GET | 获取用户详情 |
| /api/admin/users/{id}/records | GET | 获取用户录音记录 |
| /api/admin/users/export | GET | 导出用户数据 |

### 3.3 日记管理

| 接口 | 方法 | 说明 |
|-----|------|------|
| /api/admin/diaries | GET | 获取日记列表（分页/搜索） |
| /api/admin/diaries/{id} | GET | 获取日记详情（含关联记录） |
| /api/admin/diaries/export | GET | 导出日记数据 |

### 3.4 系统设置

| 接口 | 方法 | 说明 |
|-----|------|------|
| /api/admin/admin-users | GET | 获取管理员列表 |
| /api/admin/admin-users | POST | 添加管理员 |
| /api/admin/admin-users/{id}/reset-password | POST | 重置密码 |

## 4. 页面设计

### 4.1 登录页
- 用户名/密码表单
- 记住我选项
- 登录按钮

### 4.2 主布局
- 左侧：侧边栏菜单
- 顶部：标题栏 + 用户信息
- 中间：内容区

### 4.3 用户列表页
- 搜索框（用户名/手机号）
- 时间范围筛选
- 用户表格
- 导出按钮

### 4.4 用户详情页
- 用户基本信息
- 录音记录表格
- 返回按钮

### 4.5 日记列表页
- 搜索框
- 日期范围筛选
- 日记表格
- 导出按钮

### 4.6 日记详情页
- 日记基本信息
- **当天录音记录列表**
- **生成的日记内容**
- 返回按钮

### 4.7 系统设置页
- 管理员列表
- 添加管理员按钮

## 5. 开发计划

### Phase 1: 后端开发（2天）
- [ ] 项目初始化
- [ ] 数据库连接
- [ ] 登录模块
- [ ] 用户管理 API
- [ ] 日记管理 API
- [ ] 系统设置 API

### Phase 2: 前端开发（2天）
- [ ] 项目初始化
- [ ] 登录页面
- [ ] 主布局
- [ ] 用户管理页面
- [ ] 日记管理页面
- [ ] 系统设置页面

### Phase 3: 联调测试 + 部署（1天）
- [ ] 前后端联调
- [ ] 数据库只读账号配置
- [ ] 部署配置
- [ ] 测试验证

## 6. 部署说明

### 6.1 目录结构
```
/opt/echo-admin/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── nginx.conf
└── supervisor.conf
```

### 6.2 Nginx 配置
```nginx
server {
    listen 80;
    server_name admin.echo-app.com;

    location /api {
        proxy_pass http://127.0.0.1:8100;
    }

    location / {
        root /opt/echo-admin/frontend/dist;
        try_files $uri /index.html;
    }
}
```

---

**创建时间**：2026-03-07
