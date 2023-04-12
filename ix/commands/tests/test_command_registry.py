import unittest
from ix.commands import Command, CommandRegistry


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
        registry.register(cmd)

        self.assertIn("sample", registry.commands)
        self.assertEqual(registry.commands["sample"], cmd)


if __name__ == "__main__":
    unittest.main()
