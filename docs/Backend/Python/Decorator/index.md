# Python 装饰器

装饰器是接收一个函数并返回一个新函数的可调用对象，用来**在不修改原函数代码的情况下增强它的行为**。

## 最简单的装饰器

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("调用前")
        result = func(*args, **kwargs)
        print("调用后")
        return result
    return wrapper

@my_decorator
def say_hello(name):
    print(f"Hello, {name}")

say_hello("张三")
```

输出：

```text
调用前
Hello, 张三
调用后
```

`@my_decorator` 相当于执行 `say_hello = my_decorator(say_hello)`。

## 保留函数元信息：functools.wraps

装饰器里的 `wrapper` 会覆盖原函数的 `__name__`、`__doc__` 等元信息，用 `functools.wraps` 可以原样保留：

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

::: danger 注意
不写 `@wraps` 时，被装饰函数的 `__name__` 会变成 `wrapper`，影响调试、日志和文档生成，务必加上。
:::

## 带参数的装饰器

```python
from functools import wraps

def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("hi")

greet()
```

这里 `repeat(3)` 先返回真正的装饰器，再装饰 `greet`。

## 常用的内置装饰器

| 装饰器 | 作用 |
| --- | --- |
| `@staticmethod` | 静态方法，不依赖实例 |
| `@classmethod` | 类方法，第一个参数是类本身 |
| `@property` | 把方法变成属性访问器 |
| `@functools.cache` / `@functools.lru_cache` | 缓存函数结果 |
| `@dataclasses.dataclass` | 自动生成 `__init__`、`__repr__` 等 |

property 示例：

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

c = Circle(2)
print(c.area)   # 12.56636
```

缓存示例：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

## 多个装饰器叠加

```python
@decorator_a
@decorator_b
def f():
    ...
```

叠加顺序：**从下往上应用**（先包 `decorator_b`，再包 `decorator_a`），调用时**从上往下执行**。

## 实战：计时器

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时 {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer
def work():
    time.sleep(0.2)

work()
print(work.__name__)   # work，而不是 wrapper
```

验证：运行后能看到耗时输出，且 `work.__name__` 仍然是 `work`。
