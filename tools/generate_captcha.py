from concurrent.futures import ProcessPoolExecutor, as_completed
import random
import string
from typing import Iterable, List
import uuid
from pathlib import Path

from tqdm import trange, tqdm
from captcha.image import ImageCaptcha
from typer import Typer, Argument

app = Typer()

data = Path(__file__).parent / "data"
data.mkdir(parents=True, exist_ok=True)

@app.command()
def digits(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    chars: int = 4,
    font: List[Path] = (),
    font_size: List[int] = (42, 50, 56),
):
    image = ImageCaptcha(
        width=280, height=140, fonts=[str(f) for f in font], font_sizes=font_size
    )
    output.mkdir(parents=True, exist_ok=True)
    for i in trange(num, desc="Generating captchas"):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = "".join(random.choice(string.digits) for _ in range(random_chars))
        hash = str(uuid.uuid4()).replace("-", "")
        image.write(code, output / f"{code}_{hash}.png")

@app.command()
def letters(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    chars: int = 4,
    case: bool = False,
    font: List[Path] = (),
    font_size: List[int] = (42, 50, 56),
):
    image = ImageCaptcha(
        width=210, height=100, fonts=[str(f) for f in font], font_sizes=font_size
    )
    output.mkdir(parents=True, exist_ok=True)
    for i in trange(num, desc="Generating captchas"):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = "".join(
            random.choice(
                string.digits + string.ascii_lowercase + string.ascii_uppercase
            )
            for _ in range(random_chars)
        )
        hash = str(uuid.uuid4()).replace("-", "")
        spec = code.upper() if not case else code
        image.write(code, output / f"{spec}_{hash}.png")

def generate_cchars(image, code, output):
    hash = str(uuid.uuid4()).replace("-", "")
    image.write(code, output / f"{code}_{hash}.png")

@app.command()
def cchars(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    chars: int = 4,
    font: List[Path] = (),
    font_size: List[int] = (35, 40, 45, 50, 55),
):
    image = ImageCaptcha(
        width=160, height=60, fonts=[str(f) for f in font], font_sizes=font_size
    )
    output.mkdir(parents=True, exist_ok=True)
    with open(data / 'common_cchars.txt') as f:
        cchars = list(f.read().strip())
    codes = []
    for _ in trange(num, desc="Selecting codes"):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = "".join(random.choice(cchars) for _ in range(random_chars))
        codes.append(code)
    with ProcessPoolExecutor() as e:
        futures = []
        for c in codes:
            futures.append(e.submit(generate_cchars, image, c, output))
        for f in tqdm(as_completed(futures), total=len(futures), desc="Generating captchas"):
            pass
    
if __name__ == "__main__":
    app()
