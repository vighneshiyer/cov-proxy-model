"""
Combines all scripts in this folder except for compile_generator into one script.
"""
from pathlib import Path
import argparse
from generate_configs import generate_configs
from combine_scripts_single_config import call_combine_scripts_single_config
from parse_coverages import clean_csvs
from joblib import delayed, Parallel

def main():
    parser = argparse.ArgumentParser(prog="combined_scripts",
                                     description="Run all scripts in this folder in order")
    parser.add_argument('--n-configs', type=int, help="Number of configs to generate", required=True)
    parser.add_argument('--n-seeds', type=int, help="Number of unique seeds per config to generate", required=True)
    parser.add_argument('--default-prob', type=float,
                        help="The probability that each plusarg will be the default value", required=True)
    parser.add_argument('--riscv-dv-bin', help="The riscv-dv compiled binary", required=True)
    parser.add_argument('--rtl-sim-bin', help="The compiled Rocket-Chip rv32imc Verilator simulation binary", required=True)
    parser.add_argument('--config-dir', help="Path to a directory to store configs, elves, and simulation logs in", required=True)
    parser.add_argument('--out-dir', help="Path to a directory to store output CSVs in", required=True)
    parser.add_argument('--lower-bound', help="Lower bound for coverage rate", required=False, default=0)
    parser.add_argument('--upper-bound', help="Upper bound for coverage rate", required=False, default=0.90)
    args = parser.parse_args()

    generate_configs(args.config_dir, args.n_configs, args.n_seeds, args.default_prob)

    config_path = Path(args.config_dir)

    if not Path(args.out_dir).exists():
        Path(args.out_dir).mkdir()
    
    programs = []
    for config_id in config_path.iterdir():
        for seed in config_id.glob("*.json"):
            programs.append(delayed(call_combine_scripts_single_config)(
                config_path,
                config_id.name,
                seed.name.split('.')[0],
                args.riscv_dv_bin,
                args.rtl_sim_bin,
                args.out_dir
            ))
    Parallel(n_jobs=28, prefer="threads")(programs)

    clean_csvs(Path(args.out_dir), args.lower_bound, args.upper_bound)


if __name__ == "__main__":
    main()