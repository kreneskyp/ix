import unittest
from command import Command


class TestCommand(unittest.TestCase):
    def test_command(self):
        def sample_function(param1, param2):
            return param1 + param2

        cmd = Command(
            name="sample",
            description="A sample command that adds two numbers.",
            method=sample_function,
            signature="(param1: int, param2: int) -> int",
        )

        self.assertEqual(cmd.name, "sample")
        self.assertEqual(cmd.description, "A sample command that adds two numbers.")
        self.assertEqual(cmd.signature, "(param1: int, param2: int) -> int")
        self.assertEqual(cmd(3, 4), 7)


if __name__ == "__main__":
    unittest.main()
