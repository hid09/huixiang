# 回响后台管理系统 - 测试文档

## 测试报告摘要

| 指标 | 结果 |
|-----|------|
| 后端测试 | 17 passed, 36 skipped, 1 xfailed |
| 前端测试 | 3 passed, 6 skipped |
| 代码覆盖率 | 67% |
| 安全测试 | 5/5 通过 |

> 完整测试报告请查看项目根目录 `TEST_REPORT.md`

---

## 后端测试

### 本地运行（无数据库）

```bash
cd backend

# 安装测试依赖
pip install -r requirements.txt

# 运行不需要数据库的测试
pytest tests/test_auth.py tests/test_security.py -v

# 生成覆盖率报告
pytest tests/test_auth.py tests/test_security.py --cov=app --cov-report=html
```

### 服务器运行（完整测试）

#### 1. 配置数据库连接

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑 .env，设置数据库连接信息
# DB_HOST=your_db_host
# DB_PORT=3306
# DB_USER=echo_readonly
# DB_PASSWORD=your_password
# DB_NAME=echo_db
```

#### 2. 运行所有测试

```bash
# 运行所有测试（包括需要数据库的）
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_auth.py          # 认证模块
pytest tests/test_dashboard.py     # 数据看板
pytest tests/test_users.py         # 用户管理
pytest tests/test_admin_users.py   # 管理员管理
pytest tests/test_security.py      # 安全测试

# 只运行安全测试
pytest tests/test_security.py -v -m security

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 查看详细输出
pytest -v -s
```

### 测试文件结构

```
backend/tests/
├── conftest.py           # pytest 配置和 fixtures
├── test_auth.py          # 认证模块测试 (12 passed)
├── test_dashboard.py     # 数据看板测试 (需DB)
├── test_users.py         # 用户管理测试 (需DB)
├── test_admin_users.py   # 管理员管理测试 (需DB)
└── test_security.py      # 安全测试专项 (5 passed)
```

### 安全测试清单

| 测试项 | 状态 | 说明 |
|-------|------|------|
| SQL注入 | ⏭️ 需DB | 测试所有带查询参数的接口 |
| XSS | ⏭️ 需DB | 测试特殊字符是否被转义 |
| 认证绕过 | ✅ 完成 | 测试伪造token、过期token、无token |
| 权限提升 | ⏭️ 需DB | 测试普通管理员访问超管接口 |
| 弱密码 | ⏭️ 需DB | 测试密码强度验证 |
| 暴力破解 | ⏭️ 需DB | 测试速率限制 |
| 算法混淆攻击 | ✅ 完成 | None 算法攻击测试 |

---

## 前端测试

### 运行测试

```bash
cd frontend

# 安装测试依赖
npm install

# 运行所有测试
npm run test

# 运行测试UI界面
npm run test:ui

# 生成覆盖率报告
npm run test:coverage
```

### 测试文件结构

```
frontend/src/tests/
├── setup.ts              # 测试环境配置
├── test-utils.tsx        # 测试工具函数
├── mockData/
│   └── index.ts          # Mock 数据
├── pages/
│   └── Login.test.tsx    # 登录页测试
└── components/
    ├── Layout.test.tsx   # 布局组件测试
    └── Header.test.tsx   # 顶部栏测试
```

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: echo_db_test
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
        env:
          DB_HOST: 127.0.0.1
          DB_USER: root
          DB_PASSWORD: password
          DB_NAME: echo_db_test

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
```

---

## 待办事项

### 部署后验证

- [ ] 连接数据库，运行 36 个被跳过的测试
- [ ] 验证 SQL 注入防护
- [ ] 验证 XSS 防护
- [ ] 验证命令注入防护
- [ ] 验证速率限制
- [ ] 验证弱密码检测

### 覆盖率提升

- [ ] 提升整体覆盖率到 80%
- [ ] 补充 `app/api/dashboard.py` 测试（当前 28%）
- [ ] 补充 `app/services/user_service.py` 测试（当前 23%）
- [ ] 补充前端组件完整测试
