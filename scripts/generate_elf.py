import argparse
from pathlib import Path

from modeling.build import run_cmd, riscv_dv_cmd
from modeling.riscv_dv import RiscvDvConfig


def main():
    parser = argparse.ArgumentParser(prog="generate_elf",
                                     description="Generate asm for a config with riscv-dv, then compile it to a binary")
    parser.add_argument('--riscv-dv-bin', help="The riscv-dv compiled binary", required=True)
    parser.add_argument('--config', help="Path to the config JSON object", required=True)
    parser.add_argument('--out-dir', help="Where the generated files should be placed", required=True)
    parser.add_argument('--out-prefix', help="Prefix for the generated files (.S, .bin, .elf)", required=True)
    args = parser.parse_args()

    riscv_dv_bin = Path(args.riscv_dv_bin).resolve()

    (cmd, envvars) = riscv_dv_cmd(riscv_dv_bin, RiscvDvConfig.parse_raw(Path(args.config).read_text()))
    run_cmd(cmd, envvars, 30)
