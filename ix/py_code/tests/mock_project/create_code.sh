#!/bin/bash

# Creating directories
mkdir -p module1/module2/module3

# Creating files
echo "from typing import Any, Dict
from module1.module2.module3.another_class import AnotherParent

class GrandParent:
    class_variable = 'I am a class variable'

    def __init__(self):
        self.instance_variable = 'I am an instance variable'

    def method(self, arg1: Any, *args: Any, **kwargs: Any):
        print(f'GrandParent method called with {arg1}, {args}, {kwargs}')


class Parent(GrandParent):
    def method(self, arg1: Any, *args: Any, **kwargs: Any):
        print(f'Parent method called with {arg1}, {args}, {kwargs}')
        super().method(arg1, *args, **kwargs)


class Child(Parent, AnotherParent):
    def __init__(self):
        super().__init__()
        self.child_variable = 'I am a child variable'

    def child_method(self):
        parent = Parent()
        parent.method('from child method')" > module1/module2/module3/my_class.py

echo "class AnotherParent:
    def another_method(self):
        print('Another parent method called')" > module1/module2/module3/another_class.py

echo "import numpy as np
from typing import Any, Dict
from module1.module2.module3.my_class import GrandParent, Parent, Child

MODULE_LEVEL_VARIABLE = 'This is a module level variable'

def module_level_function(arg1: Any, *args: Any, **kwargs: Any) -> None:
    print(f'Module level function called with {arg1}, {args}, {kwargs}')

def another_module_level_function() -> None:
    print('Another module level function called')

def function_calls_function() -> None:
    module_level_function('Hello', 'World', key1='value1', key2='value2')
    another_module_level_function()

def function_calls_multiple_functions() -> None:
    module_level_function('Hello', 'World', key1='value1', key2='value2')
    another_module_level_function()
    repeat_class_method_calls()

def function_calls_function_in_loop() -> None:
    for i in range(3):
        module_level_function(f'Hello {i}', 'World', key1='value1', key2='value2')

def repeat_class_method_calls():
    child = Child()
    child.child_method()
    child.method('from repeat class method calls')" > utils.py

echo "import numpy as np
from module1.module2.module3.my_class import Parent, Child
from utils import MODULE_LEVEL_VARIABLE, module_level_function

print(MODULE_LEVEL_VARIABLE)
module_level_function('Hello from main')

parent = Parent()
child = Child()

parent.method('Hello from main')
child.method('Hello from main')" > main.py

echo "numpy==1.21.2" > requirements.txt

echo "def simple_decorator(func):
    def wrapper():
        print('Before function call')
        func()
        print('After function call')
    return wrapper

def decorator_with_args(arg1, arg2):
    def outer_wrapper(func):
        def inner_wrapper():
            print(f'Before function call with args {arg1}, {arg2}')
            func()
            print('After function call')
        return inner_wrapper
    return outer_wrapper

def method_decorator(method):
    def wrapper(self, *args, **kwargs):
        print('Before method call')
        method(self, *args, **kwargs)
        print('After method call')
    return wrapper

# Completing the bash script
echo "def class_decorator(cls):
    cls.decorated = True
    return cls

@class_decorator
class DecoratedClass:
    @method_decorator
    def decorated_method(self):
        print('Decorated method')" > decorators.py

echo "def generator_function():
    \"\"\"
    This is a generator function
    \"\"\"
    for i in range(3):
        yield i

def function_with_exception_handling():
    \"\"\"
    This function tests exception handling
    \"\"\"
    try:
        1 / 0
    except ZeroDivisionError:
        print('Caught an exception')
    finally:
        print('Finally block executed')

def function_with_with_statement():
    \"\"\"
    This function tests the 'with' statement
    \"\"\"
    with open('requirements.txt', 'r') as file:
        print(file.read())" >> utils.py


echo "def class_decorator(cls):
    cls.decorated = True
    return cls

@class_decorator
class DecoratedClass:
    @method_decorator
    def decorated_method(self):
        print('Decorated method')" > decorators.py

echo "def generator_function():
    \"\"\"
    This is a generator function
    \"\"\"
    for i in range(3):
        yield i

def function_with_exception_handling():
    \"\"\"
    This function tests exception handling
    \"\"\"
    try:
        1 / 0
    except ZeroDivisionError:
        print('Caught an exception')
    finally:
        print('Finally block executed')

def function_with_with_statement():
    \"\"\"
    This function tests the 'with' statement
    \"\"\"
    with open('requirements.txt', 'r') as file:
        print(file.read())" >> utils.py

echo "def class_decorator(cls):
    cls.decorated = True
    return cls

@class_decorator
class DecoratedClass:
    @method_decorator
    def decorated_method(self):
        print('Decorated method')" > decorators.py

echo "def generator_function():
    \"\"\"
    This is a generator function
    \"\"\"
    for i in range(3):
        yield i

def function_with_exception_handling():
    \"\"\"
    This function tests exception handling
    \"\"\"
    try:
        1 / 0
    except ZeroDivisionError:
        print('Caught an exception')
    finally:
        print('Finally block executed')

def function_with_with_statement():
    \"\"\"
    This function tests the 'with' statement
    \"\"\"
    with open('requirements.txt', 'r') as file:
        print(file.read())" >> utils.py
