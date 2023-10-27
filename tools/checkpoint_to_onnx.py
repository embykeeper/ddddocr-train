from pathlib import Path
import sys
import time

from typer import Typer

sys.path.append(str(Path(__file__).parent.parent))

from utils import train

app = Typer(pretty_exceptions_show_locals=False)

@app.command()
def main(project: str, num: int = 1):
    checkpoints_dir = Path(__file__).parent.parent / 'projects' / project / 'checkpoints'
    checkpoints_bak_dir = checkpoints_dir.with_name('checkpointsbak')
    checkpoints_bak_dir.mkdir(parents=True, exist_ok=True)
    checkpoints = list(sorted(checkpoints_dir.iterdir(), key=lambda f: int(f.stem.split('_')[-1])))
    for i in range(num):
        to_move = checkpoints[-i:] if i else []
        print('Move:', to_move)
        to_move = [f.rename(checkpoints_bak_dir / f.name) for f in to_move]
        time.sleep(2)
        try:
            trainer = train.Train(project)
            trainer.target_acc = 0.0
            trainer.min_epoch = 0
            trainer.max_loss = float('inf')
            trainer.test_step = 1
            try:
                trainer.start()
            except SystemExit:
                pass
        finally:
            to_move = [f.rename(checkpoints_dir / f.name) for f in to_move]
if __name__ == "__main__":
    app()
