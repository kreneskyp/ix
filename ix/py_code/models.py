from django.db import models
from ix.pg_vector.fields import VectorField


class Project(models.Model):
    """
    A model representing a Python project.
    """

    name = models.CharField(max_length=200)
    description = models.TextField()
    github_url = models.URLField()
    local_path = models.FilePathField(
        help_text="The local directory path where the project is checked out."
    )


class CodeObject(models.Model):
    """
    A model representing a Python object in a project. This can be a class, method, function, or variable.
    """

    CLASS = "CL"
    METHOD = "ME"
    FUNCTION = "FU"
    VARIABLE = "VA"

    TYPE_CHOICES = [
        (CLASS, "Class"),
        (METHOD, "Method"),
        (FUNCTION, "Function"),
        (VARIABLE, "Variable"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    start_line_number = models.PositiveIntegerField()
    end_line_number = models.PositiveIntegerField()
    file_path = models.FilePathField()
    class_path = models.CharField(max_length=500)
    file_hash = models.CharField(max_length=64)
    is_external = models.BooleanField(
        default=False, help_text="Indicates if the object is external to the project."
    )

    embeddings = VectorField(null=True)

    def __str__(self):
        return f"{self.class_path}"

    def get_source_code(self) -> str:
        """
        Retrieve the source code for this CodeObject.

        Returns:
            str: The source code.
        """
        try:
            with open(self.file_path, "r") as file:
                lines = file.readlines()
            # Python list indexes are 0-based, while line numbers are 1-based.
            # Subtract one from start_line_number and end_line_number when slicing.
            code_lines = lines[self.start_line_number - 1 : self.end_line_number]
            return "".join(code_lines)
        except FileNotFoundError:
            # Handle the exception if the file does not exist.
            print(f"File {self.file_path} not found.")
            return ""

    def print_source_code(self):
        """
        Print the source code for this CodeObject, maintaining formatting.
        """
        print(self.get_source_code())


# TODO: is this enough for both class variable/methods, class inheritance, and imports?
class Relation(models.Model):
    """
    A model representing a relation between two Python objects in a project. For example, a class and its methods.
    """

    parent = models.ForeignKey(
        CodeObject, on_delete=models.CASCADE, related_name="children"
    )
    child = models.ForeignKey(
        CodeObject, on_delete=models.CASCADE, related_name="parents"
    )
    is_import = models.BooleanField(default=False)


class Version(models.Model):
    """
    A model representing a version of a Python object in a project. This is tied to a specific git commit and branch.
    """

    code_object = models.ForeignKey(CodeObject, on_delete=models.CASCADE)
    commit = models.CharField(max_length=40)
    branch = models.CharField(max_length=200, null=True, blank=True)


class Invocation(models.Model):
    """
    A model representing an invocation of a function, method, or class.
    This can represent a function or method calling another function or method, or a function or method instantiating a class.
    """

    invoker = models.ForeignKey(
        CodeObject,
        related_name="invocations",
        on_delete=models.CASCADE,
        help_text="The function, method, or class that is invoking another code object.",
    )
    invokee = models.ForeignKey(
        CodeObject,
        related_name="invoked_by",
        on_delete=models.CASCADE,
        help_text="The function, method, or class that is being invoked.",
    )
    line_number = models.PositiveIntegerField(
        help_text="The line number where the invocation occurs."
    )
