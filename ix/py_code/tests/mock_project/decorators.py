def simple_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")

    return wrapper


def decorator_with_args(arg1, arg2):
    def outer_wrapper(func):
        def inner_wrapper():
            print(f"Before function call with args {arg1}, {arg2}")
            func()
            print("After function call")

        return inner_wrapper

    return outer_wrapper


def method_decorator(method):
    def wrapper(self, *args, **kwargs):
        print("Before method call")
        method(self, *args, **kwargs)
        print("After method call")

    return wrapper


def class_decorator(cls):
    cls.decorated = True
    return cls


@class_decorator
class DecoratedClass:
    @method_decorator
    def decorated_method(self):
        print("Decorated method")


@simple_decorator
def simple_function():
    print("Simple function")
