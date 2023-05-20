from pathlib import Path
import sys

import onnx
import torch
from onnx2pytorch import ConvertModel
from typer import Typer, Argument

sys.path.append(str(Path(__file__).parent.parent))

from utils import train

app = Typer(pretty_exceptions_show_locals=False)


@app.command()
def main(project: str, common: Path = Argument(..., dir_okay=True, exists=True)):
    trainer = train.Train(project)
    onnx_model = onnx.load(common)
    torch_model = ConvertModel(onnx_model)
    torch.save(
        {
            "net": torch_model.state_dict(),
            "optimizer": trainer.net.optimizer.state_dict(),
            "epoch": trainer.epoch,
            "step": trainer.step,
            "lr": trainer.lr,
        },
        f"checkpoint_common_1_1.tar",
    )


if __name__ == "__main__":
    app()
