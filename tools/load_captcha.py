import uuid
from pathlib import Path

from typer import Typer, Argument

app = Typer()


@app.command()
def main(inp: Path = Argument(..., exists=True, file_okay=False)):
    for f in inp.iterdir():
        hash = str(uuid.uuid4()).replace("-", "")
        print(f.with_stem(f"{f.stem.upper()}_{hash}"))
        f.rename(f.with_stem(f"{f.stem.upper()}_{hash}"))


if __name__ == "__main__":
    app()
