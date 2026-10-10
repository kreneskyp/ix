import numpy as np
from module1.module2.module3.my_class import Parent, Child
from utils import MODULE_LEVEL_VARIABLE, module_level_function

print(MODULE_LEVEL_VARIABLE)
module_level_function("Hello from main")

parent = Parent()
child = Child()

parent.method("Hello from main")
child.method("Hello from main")
