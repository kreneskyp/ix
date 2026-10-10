import ast


class ImportGatherer(ast.NodeVisitor):
    """
    Class to parse Python source code and gather imports.

    This class extends the built-in NodeVisitor class, so it defines methods that are
    called for each type of node in the AST (Abstract Syntax Tree).

    Attributes:
        imports: Dictionary mapping names used in the code to fully qualified names of imported objects.
    """

    def __init__(self):
        """
        Initialize the ImportGatherer with an empty import table.
        """
        self.imports = {}

    def visit_Import(self, node):
        """
        Visit an Import node and add its aliases to the import table.

        Args:
            node: The Import node to visit.
        """
        for alias in node.names:
            self.imports[alias.name] = alias.asname if alias.asname else alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """
        Visit an ImportFrom node and add its aliases to the import table.

        Args:
            node: The ImportFrom node to visit.
        """
        for alias in node.names:
            asname = alias.asname if alias.asname else alias.name
            self.imports[asname] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def parse_code(self, code):
        """
        Parse the given source code and gather imports.

        Args:
            code: The Python source code to parse.

        Returns:
            A dictionary mapping names used in the code to fully qualified names of imported objects.
        """
        tree = ast.parse(code)
        self.visit(tree)
        return self.imports
