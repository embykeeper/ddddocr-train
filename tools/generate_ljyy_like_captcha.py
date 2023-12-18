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

urdu_alphabets: List[str] = (
    "آ أ ا ب پ ت ٹ ث "
    " ج چ ح خ "
    " د ڈ ذ ر ڑ ز ژ "
    " س ش ص ض ط ظ ع غ "
    " ف ق ک گ ل م "
    " ن ں و ؤ ہ ۂ ۃ "
    " ھ ء ی ئ ے ۓ "
).split()

def generate_uchars(image, code, output):
    hash = str(uuid.uuid4()).replace("-", "")
    out = output / "{}_{}.png".format(code[::-1], hash)
    image.write(code, str(out))

@app.command()
def uchars(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    chars: int = 4,
    font_size: List[int] = (35, 40, 45, 50, 55),
):
    image = ImageCaptcha(
        width=160, height=60, fonts=[str(data / "IBMPlexSansArabic-Regular.ttf")], font_sizes=font_size
    )
    output.mkdir(parents=True, exist_ok=True)
    codes = []
    for _ in trange(num, desc="Selecting codes"):
        random_chars = random.randint(*chars) if isinstance(chars, Iterable) else chars
        code = "".join(random.choice(urdu_alphabets) for _ in range(random_chars))
        codes.append(code)
    with ProcessPoolExecutor() as e:
        futures = []
        for c in codes:
            futures.append(e.submit(generate_uchars, image, c, output))
        for f in tqdm(as_completed(futures), total=len(futures), desc="Generating captchas"):
            pass
    
if __name__ == "__main__":
    app()
