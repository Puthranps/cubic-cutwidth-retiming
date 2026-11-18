"""Run the supplied bench unchanged except for saving its input graph and returned order."""
import argparse
import importlib.util
from pathlib import Path
import sys

import numpy as np


def main():
    root, save, *cli = sys.argv[1:]
    save = Path(save).resolve()
    save.mkdir(parents=True, exist_ok=True)
    script = Path(root).resolve() / "research/bench/cutwidth_bench.py"
    spec = importlib.util.spec_from_file_location("supplied_cutwidth_bench", script)
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--seeds", nargs="+", type=int, default=[1])
    seeds = iter(parser.parse_known_args(cli)[0].seeds)
    original = bench.load_custom

    def capture(path):
        method = original(path)

        def wrapped(G, A, rng):
            order = method(G, A, rng)
            seed = next(seeds)
            edges = np.sort(np.asarray(G.edges, dtype=np.int32), axis=1)
            edges = edges[np.lexsort((edges[:, 1], edges[:, 0]))]
            np.savez_compressed(save / f"cubic_{len(G)}_{seed}.npz",
                                edges=edges, order=np.asarray(order, dtype=np.int32))
            return order
        return wrapped

    bench.load_custom = capture
    sys.argv = [str(script), *cli]
    bench.main()


if __name__ == "__main__":
    main()
