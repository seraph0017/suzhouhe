## AI Manga Pipeline - Makefile

.PHONY: help dev frontend backend db-up db-down db-migrate test clean

# 默认目标
help:
	@echo "AI Manga Pipeline - 可用命令:"
	@echo ""
	@echo "  make dev          - 启动前端和后端开发服务"
	@echo "  make frontend     - 仅启动前端"
	@echo "  make backend      - 仅启动后端"
	@echo "  make db-up        - 启动 Docker 数据库服务"
	@echo "  make db-down      - 停止 Docker 数据库服务"
	@echo "  make db-migrate   - 运行数据库迁移"
	@echo "  make test         - 运行测试"
	@echo "  make clean        - 清理构建文件"

# 启动开发服务
dev:
	@echo "Starting development services..."
	@make db-up
	@echo "\n启动后端服务 (新终端)..."
	@echo "  cd backend && uvicorn app.main:app --reload --port 8000"
	@echo "\n启动前端服务 (新终端)..."
	@echo "  cd frontend && npm run dev"

# 前端
frontend:
	cd frontend && npm run dev

# 后端
backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker 数据库
db-up:
	docker-compose up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5

db-down:
	docker-compose down

db-migrate:
	cd backend && alembic upgrade head

# 测试
test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v

# 清理
clean:
	@echo "Cleaning build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"
