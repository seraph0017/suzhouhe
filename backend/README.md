# AI Manga Pipeline Backend

后端服务使用 FastAPI + Python 3.11+

## 环境要求

- Python 3.11+
- PostgreSQL 16+
- Redis 7+ (用于异步任务和缓存)

## 使用 Conda 设置环境

```bash
# 创建 conda 环境
conda create -n suzhou python=3.11 -y

# 激活环境
conda activate suzhou

# 安装依赖
pip install -r requirements.txt

# 或者使用 pyproject.toml
pip install -e .
```

## 配置文件

复制环境变量文件并修改：

```bash
cp ../.env.example .env
```

## 数据库迁移

```bash
# 初始化 Alembic
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

## 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
pytest tests/ -v --cov=app
```

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── script.py
│   │   ├── chapter.py
│   │   ├── storyboard.py
│   │   ├── asset.py
│   │   ├── review.py
│   │   ├── audit_log.py
│   │   └── model_provider.py
│   ├── schemas/             # Pydantic 模式
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   ├── middleware/          # 中间件
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
├── tests/                   # 测试文件
├── requirements.txt         # 依赖列表
├── pyproject.toml          # 项目配置
└── .env                     # 环境变量
```
