import os
import subprocess
from ix.py_code.models import Project
from ix.py_code.parser.code_objects import (
    CodeObjectCreator,
    create_code_objects_for_file,
)
from ix.py_code.parser.imports import ImportGatherer
from ix.py_code.parser.invocations import InvocationCreator
from ix.py_code.parser.relations import RelationCreator


def import_project_from_dir(directory):
    """
    Create a Project instance from a directory.

    This function uses the 'git' command to get the project's Git URL and
    uses the repository name as the project name.

    Args:
        directory: The directory where the project is located.

    Returns:
        A Project instance.
    """
    # Try to get the project's Git URL
    try:
        github_url = subprocess.check_output(
            ["git", "-C", directory, "config", "--get", "remote.origin.url"],
            universal_newlines=True,
        ).strip()
    except subprocess.CalledProcessError as e:
        raise
        github_url = None

    # Use the repository name as the project name
    name = (
        github_url.split("/")[-1].replace(".git", "")
        if github_url
        else os.path.basename(directory)
    )

    print(
        f"importing Project name={name} github_url={github_url} directory={directory}"
    )

    # Create the Project instance
    project = Project.objects.create(
        name=name, github_url=github_url, local_path=directory
    )
    return project


def parse_project(project: Project):
    """
    Parse a project and create CodeObject, Relation, and Invocation instances.

    This function walks through all Python files in the project directory and
    uses the ast (Abstract Syntax Tree) module to parse the source code.

    Args:
        project: The Project instance to parse.
    """
    file_paths = []
    for root, dirs, files in os.walk(project.local_path):
        for name in files:
            if name.endswith(".py"):
                file_path = os.path.join(root, name)
                file_paths.append(file_path)

    # First pass to create CodeObjects
    for file_path in file_paths:
        with open(file_path, "r") as file:
            code = file.read()

        # Gather imports
        # import_gatherer = ImportGatherer()
        # imports = import_gatherer.parse_code(code)

        # Create CodeObjects
        # TODO: don't know where the imports were supposed to be used
        # creator = CodeObjectCreator(project, file_path, imports)
        creator = CodeObjectCreator(project, file_path)
        created_objects = creator.parse_code(code)

    # Second pass to create Relations and Invocations
    for file_path in file_paths:
        with open(file_path, "r") as file:
            code = file.read()

        # Gather imports
        import_gatherer = ImportGatherer()
        imports = import_gatherer.parse_code(code)

        # Create Relations
        relation_creator = RelationCreator(project, file_path, imports)
        relation_creator.parse_code(code)

        # Create Invocations
        invocation_creator = InvocationCreator(project, file_path, imports)
        invocation_creator.parse_code(code)
