"""
Combines all scripts in this folder except for compile_generator into one script.
"""

import argparse
from generate_configs import generate_configs
from generate_elves import generate_elves
from run_all_rtl_sims import run_all_rtl_sims
from parse_coverages import parse_coverages

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
    args = parser.parse_args()

    generate_configs(args.config_dir, args.n_configs, args.n_seeds, args.default_prob)
    generate_elves(args.riscv_dv_bin, args.config_dir)
    # TODO: figure out how to handle elf timeout errors.
    run_all_rtl_sims(args.rtl_sim_bin, args.config_dir)
    # TODO: figure out how to handle rtl simulation errors.
    parse_coverages(args.config_dir, args.out_dir)

if __name__ == "__main__":
    main()