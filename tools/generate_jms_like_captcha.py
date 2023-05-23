from math import sqrt, pow
from pathlib import Path
import random
import string
from typing import List
import uuid
import json

from loguru import logger
from PIL import Image, ImageDraw, ImageFilter
from captcha.image import ImageCaptcha
from tqdm import tqdm
from typer import Typer, Argument

app = Typer()


data = Path(__file__).parent / "data"
data.mkdir(parents=True, exist_ok=True)


class JMSCaptcha(ImageCaptcha):
    def create_captcha_image(self, chars, color, background):
        image = Image.new("RGB", (self._width, self._height), background)
        draw = ImageDraw.Draw(image)

        def _draw_character(c):
            font = random.choice(self.truefonts)
            try:
                _, _, w, h = draw.textbbox((1, 1), c, font=font)
            except AttributeError:
                w, h = draw.textsize(c, font=font)

            dx = 6
            dy = 6
            im = Image.new("RGBA", (w + dx, h + dy), color=(0, 0, 0, 0))
            ImageDraw.Draw(im).text(
                (dx, dy),
                c,
                font=font,
                fill=color,
                stroke_width=random.randint(0, 1),
                stroke_fill=color,
            )

            # rotate
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-20, 20), Image.Resampling.BILINEAR, expand=1)

            # warp
            dx = w * random.uniform(0, 0.15)
            dy = h * random.uniform(0, 0.15)
            x1 = int(random.uniform(-dx, dx))
            y1 = int(random.uniform(-dy, dy))
            x2 = int(random.uniform(-dx, dx))
            y2 = int(random.uniform(-dy, dy))
            w2 = w + abs(x1) + abs(x2)
            h2 = h + abs(y1) + abs(y2)
            data = (
                x1,
                y1,
                -x1,
                h2 - y2,
                w2 + x2,
                h2 + y2,
                w2 - x2,
                -y1,
            )
            im = im.transform((w, h), Image.Transform.QUAD, data)
            return im

        images = []
        for c in chars:
            images.append(_draw_character(c))

        text_width = int(sum([im.size[0] for im in images]) * random.randint(62, 65) / 100)

        width = max(text_width, self._width)
        height = int(self._height * width / self._width)
        image = image.resize((width, height))
        compose = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
        shadow = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))

        average = int(text_width / len(chars))
        offset = int(average * 0.1)

        for im in images:
            w, h = im.size
            position = int((height - h) / 2) + random.randint(
                -int(0.02 * height), int(0.02 * height)
            )
            compose.paste(im, (offset, position), im)
            imr = im.rotate(random.uniform(-5, 5), Image.Resampling.BILINEAR, expand=1)
            xmove = random.randint(int(0.02 * width), int(0.03 * width))
            if random.random() > 0.5:
                xmove = -xmove
            ymove = random.randint(int(0.02 * height), int(0.03 * height))
            if random.random() > 0.5:
                ymove = -ymove
            shadow.paste(imr, (offset + xmove, position + ymove), imr)
            offset = (
                offset + w + random.randint(-int(0.7 * average), -int(0.5 * average))
            )

        stroke = Image.new("RGBA", compose.size, (255, 255, 255, 255))
        compose_alpha = compose.getchannel(3).point(lambda x: 255 if x > 0 else 0)
        stroke_alpha = compose_alpha.filter(ImageFilter.MaxFilter(3))
        stroke_alpha = stroke_alpha.filter(ImageFilter.SMOOTH)
        stroke.putalpha(stroke_alpha)
        compose = Image.alpha_composite(stroke, compose)
        image.paste(shadow, (0, 0), shadow)
        image.paste(compose, (0, 0), compose)

        if width > self._width:
            image = image.resize((self._width, self._height))

        return image

    @staticmethod
    def create_random_lines(image, length):
        w, h = image.size
        while length > 2:
            l = random.randint(2, int(image.width / 3))
            length -= l
            y = random.randint(1, max(int(sqrt(l - 1)), 1))
            x = max(int(sqrt(pow(l, 2) - pow(y, 2))), 1)
            x1 = random.randint(0, w - x)
            x2 = x1 + x
            y1 = random.randint(0, h - y)
            y2 = y1 + y
            ImageDraw.Draw(image).line(((x1, y1), (x2, y2)), fill=(0, 0, 0), width=1)

    @staticmethod
    def create_random_circles(image):
        w, h = image.size
        for _ in range(random.randint(12, 20)):
            r = max(random.randint(int(image.width * 0.005), int(image.width * 0.02)), 1)
            x = random.randint(0, w)
            y = random.randint(0, h)
            p1 = (x - r, y - r)
            p2 = (x + r, y + r)
            if random.random() > 0.5:
                ImageDraw.Draw(image).ellipse((p1, p2), fill=(0, 0, 0))
            else:
                ImageDraw.Draw(image).ellipse((p1, p2), outline=(0, 0, 0), width=1)

    def generate_image(self, chars):
        background = (255, 255, 255)
        color = (0, 0, 0, 255)
        im = self.create_captcha_image(chars, color, background)
        self.create_random_lines(im, self._width * 4)
        self.create_random_circles(im)
        im = im.filter(ImageFilter.SHARPEN)
        return im


@app.command()
def digits(
    output: Path = Argument(..., file_okay=False),
    num: int = 10000,
    font_size: List[int] = [140, 150, 160],
):
    image = JMSCaptcha(
        width=256, height=128, fonts=[str(data / "仿宋.ttf")], font_sizes=font_size
    )
    with open(data / "idiom.json") as f:
        idioms_data = json.load(f)
    idioms = []
    for record in idioms_data:
        if not "word" in record:
            continue
        word = record["word"]
        if len(word) != 4:
            continue
        idioms.append(word)
    words = random.choices(idioms, k=num)
    logger.info(f"已读取 {len(idioms)} 条成语, 随机选取 {len(words)} 条成语.")
    output.mkdir(parents=True, exist_ok=True)

    for w in tqdm(words, desc="Generating captchas"):
        r = "".join(random.choice(string.digits) for _ in range(3))
        hash = str(uuid.uuid4()).replace("-", "")
        image.write(w[0] + r[0] + w[1] + r[1] + w[2] + r[2] + w[3], output / f"{w}_{hash}.png")


if __name__ == "__main__":
    app()
