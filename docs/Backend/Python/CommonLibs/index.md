# Python 常用第三方库

按使用场景选库，避免重复造轮子。安装命令以 uv 为例：

```shell
uv add <包名>
```

## 场景选型表

| 场景 | 推荐库 | 说明 |
| --- | --- | --- |
| HTTP 请求 | `requests` / `httpx` | `requests` 同步；`httpx` 支持异步 |
| 数据校验与模型 | `pydantic` | 类型校验、配置解析、FastAPI 默认依赖 |
| 命令行美化 | `rich` | 彩色输出、表格、进度条 |
| 网页解析 | `beautifulsoup4` / `lxml` | 配合 `requests` / `httpx` 做爬虫 |
| 数据库 | `pymysql` / `psycopg` / `sqlalchemy` | MySQL / PostgreSQL / ORM |
| 测试 | `pytest` | 主流测试框架，fixture、参数化 |
| 代码质量 | `ruff` | 同时承担 lint 和格式化 |
| 环境与依赖 | `uv` | 包、虚拟环境、Python 版本管理 |

## httpx：支持异步的 HTTP 客户端

```python
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://httpbin.org/json")
        print(r.status_code)
        print(r.json())
```

## pydantic：数据校验

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

u = User(name="张三", age=18)
print(u.model_dump())
# {'name': '张三', 'age': 18}
```

::: danger 注意
`pydantic v2` 中 `model_dump()` 替代了旧版的 `dict()`；不要使用已过时的写法。
:::

## rich：命令行美化

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="用户列表")
table.add_column("姓名")
table.add_column("年龄")
table.add_row("张三", "18")
table.add_row("李四", "20")
console.print(table)
```

## ruff：代码检查与格式化

```shell
ruff check .        # 检查问题
ruff check . --fix  # 自动修复
ruff format .       # 格式化
```

::: tip
新项目推荐组合：**uv 管理环境 + ruff 检查格式 + pytest 测试**，这是一套比较现代的 Python 工程实践。
:::
