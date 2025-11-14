#!/bin/bash
set -e

echo "=== Soul MVP 容器启动脚本 ==="

# 等待数据库就绪
echo "等待数据库连接..."
max_retries=30
retry_count=0

until python -c "
import sys
sys.path.insert(0, '/app')
from app.data.dal import get_db
from sqlalchemy import text
try:
    db = next(get_db())
    db.execute(text('SELECT 1'))
    print('数据库连接成功')
except Exception as e:
    print(f'数据库连接失败: {e}')
    sys.exit(1)
" 2>/dev/null; do
  retry_count=$((retry_count + 1))
  if [ $retry_count -ge $max_retries ]; then
    echo "✗ 数据库连接超时，已重试 $max_retries 次"
    exit 1
  fi
  echo "数据库未就绪，等待5秒后重试... ($retry_count/$max_retries)"
  sleep 5
done

echo "✓ 数据库已就绪"

# 初始化数据库表
echo "初始化数据库表..."
if python init_db.py; then
    echo "✓ 数据库表初始化成功"
else
    echo "✗ 数据库表初始化失败"
    exit 1
fi

# 创建Soul角色
echo "创建Soul角色..."
if python create_soul.py; then
    echo "✓ Soul角色创建完成"
else
    echo "⚠ Soul角色创建失败（可能已存在，继续启动）"
    # 不退出，允许继续启动（可能是重复创建）
fi

# 启动应用
echo "启动应用服务器..."
exec python start_server.py

