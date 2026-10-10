import ast
import os

from ix.py_code.models import CodeObject, Invocation


class InvocationCreator(ast.NodeVisitor):
    """
    Class to parse Python source code and create invocations between CodeObjects.

    This class extends the built-in NodeVisitor class, so it defines methods that are
    called for each type of node in the AST (Abstract Syntax Tree).

    Attributes:
        project: The Project instance associated with the source code being parsed.
        file_path: The path of the file being parsed.
        imports: Dictionary mapping names used in the code to fully qualified names of imported objects.
        current_object: The CodeObject currently being visited.
    """

    def __init__(self, project, file_path, imports):
        """
        Initialize the InvocationCreator with the given project, file path, and import data.

        Args:
            project: The Project instance associated with the source code being parsed.
            file_path: The path of the file being parsed.
            imports: Dictionary mapping names used in the code to fully qualified names of imported objects.
        """
        self.project = project
        self.file_path = file_path
        self.imports = imports
        self.current_object = None
        self.current_class = None  # Keep track of the current class

    def visit_ClassDef(self, node):
        """
        Visit a ClassDef node and its children.

        Args:
            node: The ClassDef node to visit.
        """
        old_class = self.current_class
        self.current_class = node
        self.current_object = self.find_code_object(node, CodeObject.CLASS)
        self.generic_visit(node)
        self.current_object = None
        self.current_class = old_class  # Restore the current class when exiting

    def visit_FunctionDef(self, node):
        """
        Visit a FunctionDef node and its children.

        Args:
            node: The FunctionDef node to visit.
        """
        self.current_object = self.find_code_object(node, "function")
        self.generic_visit(node)
        self.current_object = None

    def visit_Call(self, node):
        """
        Visit a Call node and create an Invocation if applicable.

        Args:
            node: The Call node to visit.
        """
        # Only create invocations if inside a class or function
        if self.current_object is not None:
            # Ensure the function name is an identifier before proceeding
            if isinstance(node.func, ast.Name):
                print(self.current_object, node, node.func)
                invoked_object = self.find_code_object_by_name(node.func.id)
                if invoked_object is not None:
                    print("Creating invocation")
                    Invocation.objects.get_or_create(
                        invoker=self.current_object, invokee=invoked_object
                    )
        self.generic_visit(node)

    def find_code_object(self, node, obj_type):
        """
        Find the CodeObject instance corresponding to the given node and type.

        Args:
            node: The node to find the CodeObject for.
            obj_type: The type of the object ('class' or 'function').

        Returns:
            The CodeObject instance if found, otherwise None.
        """
        classpath = self.get_class_path(node)
        return CodeObject.objects.filter(
            project=self.project, class_path=classpath, type=obj_type
        ).first()

    def find_code_object_by_name(self, name):
        """
        Find the CodeObject instance corresponding to the given name.

        If the name is in the import table, it is replaced with the fully qualified name.

        Args:
            name: The name to find the CodeObject for.

        Returns:
            The CodeObject instance if found, otherwise None.
        """
        if "." in name:
            name = name.split(".")[0]

        if name in self.imports:
            return None
            name = self.imports[name]
        print(f"finding code object by name: {name}")
        return CodeObject.objects.filter(project=self.project, class_path=name).first()

    def get_class_path(self, node):
        relative_path = os.path.relpath(self.file_path, self.project.local_path)
        module_name = os.path.splitext(relative_path)[0].replace(os.sep, ".")
        if isinstance(node, ast.ClassDef):
            return f"{module_name}.{node.name}"
        elif isinstance(node, ast.FunctionDef):
            return (
                f"{module_name}.{self.current_class.name}.{node.name}"
                if self.current_class
                else f"{module_name}.{node.name}"
            )

    def parse_code(self, code):
        """
        Parse the given source code and create invocations between CodeObjects.

        Args:
            code: The Python source code to parse.
        """
        tree = ast.parse(code)
        self.visit(tree)
