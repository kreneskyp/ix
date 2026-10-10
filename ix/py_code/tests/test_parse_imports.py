import pytest


from ix.py_code.parser.imports import ImportGatherer


@pytest.fixture
def import_gatherer():
    return ImportGatherer()


class TestImportGatherer:
    def test_import(self, import_gatherer):
        code = "import math"
        imports = import_gatherer.parse_code(code)
        assert imports == {"math": "math"}

    def test_import_as(self, import_gatherer):
        code = "import math as m"
        imports = import_gatherer.parse_code(code)
        assert imports == {"m": "math"}

    def test_from_import(self, import_gatherer):
        code = "from os import path"
        imports = import_gatherer.parse_code(code)
        assert imports == {"path": "os.path"}

    def test_from_import_as(self, import_gatherer):
        code = "from os import path as p"
        imports = import_gatherer.parse_code(code)
        assert imports == {"p": "os.path"}

    def test_multiple_imports(self, import_gatherer):
        code = "import math\n" "import os\n" "from sys import argv"
        imports = import_gatherer.parse_code(code)
        assert imports == {"math": "math", "os": "os", "argv": "sys.argv"}

    def test_local_import_in_function(self, import_gatherer):
        code = "def my_func():\n" "    import math"
        imports = import_gatherer.parse_code(code)
        assert imports == {"math": "math"}

    def test_local_import_in_method(self, import_gatherer):
        code = (
            "class MyClass:\n"
            "    def my_method(self):\n"
            "        from os import path"
        )
        imports = import_gatherer.parse_code(code)
        assert imports == {"path": "os.path"}
