from pathlib import Path
import sys

from typer import Typer

sys.path.append(str(Path(__file__).parent.parent))

from utils import train

app = Typer(pretty_exceptions_show_locals=False)


@app.command()
def main(project: str):
    trainer = train.Train(project)
    trainer.target_acc = 0.0
    trainer.min_epoch = 0
    trainer.max_loss = float('inf')
    trainer.test_step = 1
    trainer.start()
    
    
if __name__ == "__main__":
    app()
