from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import random
from typing import List
import uuid

from PIL import Image, ImageDraw, ImageFont
from mpire import WorkerPool
from typer import Typer, Argument

app = Typer(pretty_exceptions_show_locals=False)

data = Path(__file__).parent / "data"
data.mkdir(parents=True, exist_ok=True)

def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b

def generate(output, word, font_size):
    image = Image.new('RGB', (370, 140), random_color())
    draw = ImageDraw.Draw(image)
    font_file = str(data / 'Aa楷宋.ttf')
    font = ImageFont.truetype(font_file, size=font_size)
    tw, th = draw.textsize(word, font)
    tx = (image.width - tw) // 2
    ty = (image.height - th) // 2
    draw.text((tx, ty), word, fill=(0, 0, 0), font=font)
    image.save(output)
    
@app.command()
def chars(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    font_size: List[int] = [70],
):
    with open(data / "hard.txt") as f:
        hard = f.read().splitlines()
    output.mkdir(parents=True, exist_ok=True)
    args = []
    for _ in range(num):
        #word = "".join(random.choice(hard) for _ in range(4))
        word = "鬘壙殒黿"
        fs = random.choice(font_size)
        hash = str(uuid.uuid4()).replace("-", "")
        o = output / f"{word}_{hash}.png"
        args.append((str(o), word, fs))
    with WorkerPool() as pool:
        for i in pool.imap_unordered(generate, args, progress_bar=True):
            pass

if __name__ == "__main__":
    app()
