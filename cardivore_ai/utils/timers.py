import time
from functools import wraps

def timeit(func):
    """Decorator to measure and print execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper
