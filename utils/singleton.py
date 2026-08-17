from collections.abc import Callable
from typing import Any


def singleton[T](cls: type[T]) -> Callable[..., T]:
    instances: dict[type[T], T] = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
