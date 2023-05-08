import random
import string
from typing import Iterable, List
import uuid
from pathlib import Path

from tqdm import trange
from captcha.image import ImageCaptcha
from typer import Typer, Argument

app = Typer()

@app.command()
def digits(output: Path = Argument(..., file_okay=False), num: int = 10000, chars: int = 4, font: List[Path]=(), font_size: List[int]=(42, 50, 56)):
    image = ImageCaptcha(width=280, height=140, fonts=[str(f) for f in font], font_sizes=font_size)
    output.mkdir(parents=True, exist_ok=True)
    for i in trange(num, desc='Generating captchas'):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = ''.join(random.choice(string.digits) for _ in range(random_chars))
        hash = str(uuid.uuid4()).replace('-', '')
        image.write(code, output / f'{code}_{hash}.png')
        
@app.command()
def words(output: Path = Argument(..., file_okay=False), num: int = 10000, chars: int = 4, case: bool = False, font: List[Path]=(), font_size: List[int]=(42, 50, 56)):
    image = ImageCaptcha(width=280, height=140, fonts=[str(f) for f in font], font_sizes=font_size)
    output.mkdir(parents=True, exist_ok=True)
    for i in trange(num, desc='Generating captchas'):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = ''.join(random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for _ in range(random_chars))
        hash = str(uuid.uuid4()).replace('-', '')
        spec = code.upper() if not case else code
        image.write(code, output / f'{spec}_{hash}.png')

if __name__ == '__main__':
    app()