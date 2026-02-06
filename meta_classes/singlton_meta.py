from threading import Lock
from typing import Dict, Type, Any


class SingletonMeta(type):
    """Thread-safe implementation of Singleton using metaclass"""
    _class_instances: Dict[Type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._class_instances:  # Thread-safe checking for first thread
            with cls._lock:
                if cls not in cls._class_instances:  # Thread-safe double-checking for pending threads
                    new_class_inst = super().__call__(*args, **kwargs)
                    cls._class_instances[cls] = new_class_inst
        return cls._class_instances[cls]
