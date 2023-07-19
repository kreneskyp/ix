def write_output(text: str) -> None:
    """mock target for tests.  Mock this to capture output from echo"""
    pass


def echo(output: str) -> str:
    write_output(f"ECHO: {output}")
    return output
