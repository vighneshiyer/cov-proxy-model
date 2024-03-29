import argparse
from pathlib import Path

from modeling.riscv_dv import gen_config

def generate_configs(out_dir, n_configs, n_seeds, default_prob):
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(exist_ok=True)
    for config_idx in range(n_configs):
        (out_dir / str(config_idx)).mkdir(exist_ok=True)
        for seed in range(n_seeds):
            config = gen_config(default_prob, seed + 1)  # use the index itself as the seed (must be > 0)
            (out_dir / str(config_idx) / f"{seed}.json").write_text(config.json())

def main():
    parser = argparse.ArgumentParser(prog="generate_configs",
                                     description="Generate a bunch of RISC-DV configs as JSON")
    parser.add_argument('--out-dir', help="Directory into which each config is placed in its own subdirectory",
                        required=True)
    parser.add_argument('--n-configs', type=int, help="Number of configs to generate", required=True)
    parser.add_argument('--n-seeds', type=int, help="Number of unique seeds per config to generate", required=True)
    parser.add_argument('--default-prob', type=float,
                        help="The probability that each plusarg will be the default value", required=True)
    args = parser.parse_args()

    generate_configs(args.out_dir, args.n_configs, args.n_seeds, args.default_prob)

if __name__ == "__main__":
    main()