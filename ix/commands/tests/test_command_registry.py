import unittest
from command import Command
from command_registry import CommandRegistry


class TestCommandRegistry(unittest.TestCase):
    def test_register_command(self):
        def sample_function(param1, param2):
            return param1 + param2

        cmd = Command(
            name="sample",
            description="A sample command that adds two numbers.",
            method=sample_function,
            signature="(param1: int, param2: int) -> int",
        )

        registry = CommandRegistry()
        registry.register_command(cmd)

        self.assertIn("sample", registry.commands)
        self.assertEqual(registry.commands["sample"], cmd)

    def test_modify_command(self):
        def sample_function(param1, param2):
            return param1 + param2

        cmd = Command(
            name="sample",
            description="A sample command that adds two numbers.",
            method=sample_function,
            signature="(param1: int, param2: int) -> int",
        )

        def modified_function(param1, param2):
            return param1 * param2

        modified_cmd = Command(
            name="sample",
            description="A modified sample command that multiplies two numbers.",
            method=modified_function,
            signature="(param1: int, param2: int) -> int",
        )

        registry = CommandRegistry()
        registry.register_command(cmd)
        registry.modify_command("sample", modified_cmd)

        self.assertIn("sample", registry.commands)
        self.assertEqual(registry.commands["sample"], modified_cmd)


if __name__ == "__main__":
    unittest.main()
