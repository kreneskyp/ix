import os
import ast

from ix.py_code.models import Relation, CodeObject


def get_class_path(file_path, node):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    if isinstance(node, ast.ClassDef):
        return f"{module_name}.{node.name}"
    elif isinstance(node, ast.FunctionDef):
        return f"{module_name}.{node.name}"


class RelationCreator(ast.NodeVisitor):
    """
    Class to parse Python source code and create relations between CodeObjects.

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
        Initialize the RelationCreator with the given project, file path, and import data.

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
        self.relations = []

    def visit_ClassDef(self, node):
        """
        Visit a ClassDef node and its children, creating relations for child classes and methods.

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
        Visit a FunctionDef node and create a relation if it's a method.

        Args:
            node: The FunctionDef node to visit.
        """
        if self.current_class:
            # If there is a current class, this is a method
            obj_type = CodeObject.METHOD
        else:
            # Otherwise, it's a standalone function
            obj_type = CodeObject.FUNCTION

        function_object = self.find_code_object(node, obj_type)
        if self.current_object is not None and function_object is not None:
            self.create_relation(self.current_object, function_object)
        self.generic_visit(node)

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

    def create_relation(self, parent, child):
        """
        Create a relation between two CodeObjects, indicating whether the relation is due to an import.

        Args:
            parent: The parent CodeObject.
            child: The child CodeObject.
        """
        is_import = child.name in self.imports
        self.relations.append(
            {
                "parent": parent,
                "child": child,
                "is_import": is_import,
            }
        )

    def parse_code(self, code):
        """
        Parse the given source code and create relations between CodeObjects.

        Args:
            code: The Python source code to parse.
        """
        tree = ast.parse(code)
        self.visit(tree)
        return self.relations

    def parse_into_db(self, code):
        relations = self.parse_code(code)
        instances = [Relation(**relation) for relation in relations]
        return Relation.objects.bulk_create(instances)
