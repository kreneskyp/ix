from typing import Any, Dict
from module1.module2.module3.another_class import AnotherParent


class GrandParent:
    class_variable = "I am a class variable"

    def __init__(self):
        self.instance_variable = "I am an instance variable"

    def method(self, arg1: Any, *args: Any, **kwargs: Any):
        print(f"GrandParent method called with {arg1}, {args}, {kwargs}")


class Parent(GrandParent):
    def method(self, arg1: Any, *args: Any, **kwargs: Any):
        print(f"Parent method called with {arg1}, {args}, {kwargs}")
        super().method(arg1, *args, **kwargs)


class Child(Parent, AnotherParent):
    def __init__(self):
        super().__init__()
        self.child_variable = "I am a child variable"

    def child_method(self):
        parent = Parent()
        parent.method("from child method")

    def child_method_with_assert(self):
        parent = Parent()
        parent.method("from child method")

        # multi-line asserts are tricky for ast to parse
        assert 1 == 1
