import numpy as np
from typing import Any, Dict
from module1.module2.module3.my_class import GrandParent, Parent, Child

MODULE_LEVEL_VARIABLE = "This is a module level variable"


def module_level_function(arg1: Any, *args: Any, **kwargs: Any) -> None:
    print(f"Module level function called with {arg1}, {args}, {kwargs}")


def another_module_level_function() -> None:
    print("Another module level function called")


def function_calls_function() -> None:
    module_level_function("Hello", "World", key1="value1", key2="value2")
    another_module_level_function()


def function_calls_multiple_functions() -> None:
    module_level_function("Hello", "World", key1="value1", key2="value2")
    another_module_level_function()
    repeat_class_method_calls()


def function_calls_function_in_loop() -> None:
    for i in range(3):
        module_level_function(f"Hello {i}", "World", key1="value1", key2="value2")


def repeat_class_method_calls():
    child = Child()
    child.child_method()
    child.method("from repeat class method calls")


def generator_function():
    """
    This is a generator function
    """
    for i in range(3):
        yield i


def function_with_exception_handling():
    """
    This function tests exception handling
    """
    try:
        1 / 0
    except ZeroDivisionError:
        print("Caught an exception")
    finally:
        print("Finally block executed")


def function_with_with_statement():
    """
    This function tests the 'with' statement
    """
    with open("requirements.txt", "r") as file:
        print(file.read())
