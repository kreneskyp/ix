from pathlib import Path
import logging
import pytest
from ix.py_code.models import CodeObject, Project
from ix.py_code.parser.code_objects import (
    create_code_objects_for_file,
    create_code_objects_for_project,
)

logger = logging.getLogger(__name__)


# Test data
TEST_PROJECT = "Mock Project"
TEST_PROJECT_ROOT = Path("/var/app/ix/py_code/tests/mock_project")
TEST_FILE_PATH = TEST_PROJECT_ROOT / "module1/module2/module3/my_class.py"

MOCK_PROJECT = "ix.py_code.tests.mock_project"


def fake_project():
    return Project.objects.create(
        name=TEST_PROJECT,
        description="Test project",
        local_path=TEST_PROJECT_ROOT,
        github_url="fake@fake.com",
    )


@pytest.mark.django_db
class TestASTParser:
    @pytest.fixture(autouse=True, scope="function")
    def mock_project(self):
        project = fake_project()
        create_code_objects_for_project(project)
        yield project

    @pytest.mark.skip("not implemented yet")
    def test_can_parse_module(self, mock_project):
        print(CodeObject.objects.filter(class_path__contains="module3"))
        code_object = CodeObject.objects.get(class_path="module1.module2.module3")
        assert code_object.name == "module3"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [43, 45]
        assert code_object.project == mock_project
        assert Path(code_object.file_path) == TEST_FILE_PATH

    def test_can_parse_class(self, mock_project):
        print(CodeObject.objects.filter(class_path__contains="Child"))
        code_object = CodeObject.objects.get(
            class_path="module1.module2.module3.my_class.Child"
        )
        assert code_object.name == "Child"
        coords = [code_object.start_line_number, code_object.end_line_number]
        logger.debug("asdfasdfasfd")
        assert coords == [21, 37]
        assert code_object.project == mock_project
        assert Path(code_object.file_path) == TEST_FILE_PATH

    def test_can_parse_method(self, mock_project):
        print(CodeObject.objects.filter(class_path__contains="child_method"))

        code_object = CodeObject.objects.get(
            class_path="module1.module2.module3.my_class.Child.child_method"
        )
        assert code_object.name == "child_method"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [26, 28]
        assert code_object.project == mock_project
        assert Path(code_object.file_path) == TEST_FILE_PATH

    def test_can_parse_method_with_multiline_assert(self, mock_project):
        print(CodeObject.objects.filter(class_path__contains="child_method"))

        code_object = CodeObject.objects.get(
            class_path="module1.module2.module3.my_class.Child.child_method_with_assert"
        )
        assert code_object.name == "child_method_with_assert"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [30, 37]
        assert code_object.project == mock_project
        assert Path(code_object.file_path) == TEST_FILE_PATH

    @pytest.mark.skip("not implemented yet")
    def test_can_parse_module_level_variable(self, mock_project):
        print(CodeObject.objects.filter(class_path__contains="MODULE_LEVEL_VARIABLE"))

        code_object = CodeObject.objects.get(class_path="utils.MODULE_LEVEL_VARIABLE")
        assert code_object.name == "MODULE_LEVEL_VARIABLE"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [43, 45]
        assert code_object.project == mock_project
        assert Path(code_object.file_path) == TEST_FILE_PATH

    def test_can_parse_function(self, mock_project):
        code_object = CodeObject.objects.get(class_path="utils.module_level_function")
        assert code_object.name == "module_level_function"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [8, 9]
        assert code_object.project == mock_project
        assert Path(code_object.file_path) == TEST_PROJECT_ROOT / "utils.py"

    def test_can_parse_decorated_class(self, mock_project):
        code_object = CodeObject.objects.get(class_path="decorators.DecoratedClass")
        assert code_object.name == "DecoratedClass"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [36, 40]
        assert code_object.project == mock_project
        assert code_object

    def test_can_parse_decorated_function(self, mock_project):
        code_object = CodeObject.objects.get(class_path="decorators.simple_function")
        assert code_object.name == "simple_function"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [43, 45]
        assert code_object.project == mock_project
        assert code_object

    def test_can_parse_decorated_method(self, mock_project):
        code_object = CodeObject.objects.get(
            class_path="decorators.DecoratedClass.decorated_method"
        )
        assert code_object.name == "decorated_method"
        coords = [code_object.start_line_number, code_object.end_line_number]
        assert coords == [38, 40]
        assert code_object.project == mock_project
        assert code_object
