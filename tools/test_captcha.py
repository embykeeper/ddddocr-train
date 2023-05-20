from pathlib import Path

from ddddocr import DdddOcr
from typer import Typer, Argument
from PIL import Image

app = Typer()


@app.command()
def main(
    proj: Path = Argument(..., exists=True, file_okay=False),
    inp: Path = Argument(..., exists=True),
):
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
        print(f"{inp.name}: {captcha}")


if __name__ == "__main__":
    app()
