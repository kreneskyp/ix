from ix.commands import command


def write_output(text: str) -> None:
    """mock target for tests.  Mock this to capture output from echo"""
    pass


@command(name="echo", description="Mock command that echos")
def echo(output: str) -> str:
    write_output(f"ECHO: {output}")
    return output


@command(name="noop", description="Mock test command.")
def noop() -> None:
    return None


@command(name="fail", description="Mock test command that fails.")
def fail() -> None:
    raise Exception("This is a test failure")