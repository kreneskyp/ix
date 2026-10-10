import ast
import os
import hashlib
from ix.py_code.models import CodeObject


class CodeObjectCreator(ast.NodeVisitor):
    def __init__(self, project, file_path):
        self.project = project
        self.file_path = file_path
        self.created_code_objects = []  # Keep track of created CodeObjects
        self.current_class = None  # Keep track of the current class

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node
        self.create_code_object(
            node, CodeObject.CLASS, start_lineno=self.get_node_start_lineno(node)
        )
        self.generic_visit(node)
        self.current_class = old_class  # Restore the current class when exiting

    def visit_FunctionDef(self, node):
        self.create_code_object(
            node,
            CodeObject.FUNCTION if self.current_class is None else CodeObject.METHOD,
            start_lineno=self.get_node_start_lineno(node),
        )
        self.generic_visit(node)

    def create_code_object(self, node, obj_type, start_lineno):
        with open(self.file_path, "rb") as f:
            bytes = f.read()
            file_hash = hashlib.sha256(bytes).hexdigest()

        code_object, created = CodeObject.objects.get_or_create(
            project=self.project,
            class_path=self.get_class_path(node),
            defaults=dict(
                name=node.name,
                type=obj_type,
                start_line_number=start_lineno,
                end_line_number=self.get_node_end_lineno(node),
                file_path=self.file_path,
                file_hash=file_hash,
            ),
        )

        if created:
            self.created_code_objects.append(code_object)

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

    def get_node_start_lineno(self, node):
        """
        Get the start line number of an AST node.
        If the node has decorators, it returns the first line of the decorators;
        otherwise, it returns the first line of the node.
        """
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
            return node.decorator_list[0].lineno
        else:
            return node.lineno

    def get_node_end_lineno(self, node):
        """
        Get the end line number of an AST node.
        This version checks all descendants of the node, not just the direct children,
        so it can handle nodes with multiline strings or other complex structures.
        """
        if not hasattr(node, "lineno"):
            return -1

        def _get_node_end_lineno(node):
            if isinstance(node, ast.Str):  # Multiline strings
                return node.lineno + node.s.count("\n")
            elif isinstance(
                node, (ast.Compare, ast.Assert, ast.Expr)
            ):  # Nodes that can contain multiline strings
                return max(
                    (
                        _get_node_end_lineno(child)
                        for child in ast.iter_child_nodes(node)
                        if hasattr(child, "lineno")
                    ),
                    default=node.lineno,
                )
            elif isinstance(node, ast.arguments):  # Special case for function arguments
                return -1  # Ignore these nodes
            else:
                return max(
                    (
                        _get_node_end_lineno(child)
                        for child in ast.iter_child_nodes(node)
                        if hasattr(child, "lineno")
                    ),
                    default=node.lineno,
                )

        return _get_node_end_lineno(node)

    def parse_code(self, code):
        """
        Parse the given source code and create relations between CodeObjects.

        Args:
            code: The Python source code to parse.
        """
        tree = ast.parse(code)
        self.visit(tree)


def create_code_objects_for_file(project, file_path):
    with open(file_path, "r") as f:
        code = f.read()

    tree = ast.parse(code)
    visitor = CodeObjectCreator(project, file_path)
    visitor.visit(tree)

    return visitor.created_code_objects


def create_code_objects_for_project(project):
    code_objects = []
    for dirpath, dirnames, filenames in os.walk(project.local_path):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                code_objects.extend(create_code_objects_for_file(project, file_path))
    return code_objects
