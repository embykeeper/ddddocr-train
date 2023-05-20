import json
from pathlib import Path

from loguru import logger
from ddddocr import DdddOcr
from typer import Typer, Argument
from PIL import Image
from thefuzz import process, fuzz

app = Typer()

data = Path(__file__).parent / "data"
data.mkdir(parents=True, exist_ok=True)

@app.command()
def main(
    proj: Path = Argument(..., exists=True, file_okay=False),
    inp: Path = Argument(..., exists=True),
):
    with open(data/"idiom.txt") as f:
        idioms = f.read().splitlines()
    idioms = [i for i in idioms if len(i) == 4]
    
    # with open(data / "idiom.json") as f:
    #     idioms_data = json.load(f)
    # idioms = []
    # for record in idioms_data:
    #     if not "word" in record:
    #         continue
    #     word = record["word"]
    #     if len(word) != 4:
    #         continue
    #     idioms.append(word)
    # logger.info(f"已读取 {len(idioms)} 条成语.")
    
    if inp.is_file():
        inps = [inp]
    else:
        inps = list(inp.iterdir())
    for inp in inps:
        model = next((proj / "models").glob("*.onnx"))
        charsets = proj / "models" / "charsets.json"
        ocr = DdddOcr(
            show_ad=False, import_onnx_path=str(model), charsets_path=str(charsets)
        )
        captcha = ocr.classification(Image.open(inp))
        phrase, score = process.extractOne(captcha, idioms, scorer=fuzz.partial_token_sort_ratio)
        if score > 70 or len(captcha) < 4:
            result = phrase
        else:
            result = captcha
        correct = inp.name.split('_')[0] == result
        print(f"{inp.name}: {captcha} -> {result} {'(正确)' if correct else '(错误)'}")


if __name__ == "__main__":
    app()
