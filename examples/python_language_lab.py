"""New original teaching examples for Python 3.12; no claimed project history."""
from abc import ABC, abstractmethod
from functools import wraps
import time

def first_even(values):
    found = None
    for value in values:
        if value % 2 == 0:
            found = value
            break
    return found

def odd_only(values):
    result = []
    for value in values:
        if value % 2 == 0:
            continue
        result.append(value)
    return result

def square_stream(values):
    for value in values:
        yield value * value

def append_name(name, names=None):
    names = [] if names is None else names
    names.append(name)
    return names

def timer(record):
    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            started = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                record(func.__name__, time.perf_counter() - started)
        return wrapped
    return decorate

def retry_timeout(max_attempts=3, base_delay=0.1, sleep=time.sleep):
    """Small bounded retry lab. No jitter, deadline or side-effect guarantee."""
    if type(max_attempts) is not int or max_attempts < 1 or base_delay < 0:
        raise ValueError("invalid retry policy")
    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TimeoutError:
                    if attempt + 1 == max_attempts:
                        raise
                    sleep(base_delay * 2**attempt)
        return wrapped
    return decorate

def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

class Counter:
    category = "teaching"
    def __init__(self, name):
        self.name = name
        self.value = 0
    def read(self):
        return self.value
    def increment(self):
        self.value = self.read() + 1
        return self.value

class Created:
    def __new__(cls, events):
        events.append("new")
        return super().__new__(cls)
    def __init__(self, events):
        events.append("init")

class Factory:
    def __new__(cls):
        return {"different_type": True}
    def __init__(self):
        raise AssertionError("should not run for a dict return")

class Account:
    def __init__(self):
        self.__balance = 0
    @property
    def balance(self):
        return self.__balance
    def deposit(self, units):
        if type(units) is not int or units <= 0:
            raise ValueError("units must be a positive integer")
        self.__balance += units

class Renderer(ABC):
    @abstractmethod
    def render(self):
        pass

class TextRenderer(Renderer):
    def render(self):
        return "text"

def render_any(renderer):
    return renderer.render()
