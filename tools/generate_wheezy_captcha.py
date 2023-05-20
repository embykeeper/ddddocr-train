import random
import string
from typing import Iterable, List
import uuid
from pathlib import Path

from tqdm import trange
from captcha.image import WheezyCaptcha
from typer import Typer, Argument

app = Typer()


@app.command()
def digits(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    chars: int = 4,
    font: List[Path] = (),
):
    image = WheezyCaptcha(width=280, height=140, fonts=[str(f) for f in font])
    output.mkdir(parents=True, exist_ok=True)
    for i in trange(num, desc="Generating captchas"):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = "".join(random.choice(string.digits) for _ in range(random_chars))
        hash = str(uuid.uuid4()).replace("-", "")
        image.write(code, output / f"{code}_{hash}.png")


if __name__ == "__main__":
    app()
