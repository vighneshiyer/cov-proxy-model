import argparse
from pathlib import Path
from subprocess import TimeoutExpired
import sys

from modeling.build import run_cmd, riscv_dv_cmd, gcc_cmd
from modeling.riscv_dv import RiscvDvConfig


def main():
    parser = argparse.ArgumentParser(prog="generate_elf",
                                     description="Generate asm for a config with riscv-dv, then compile it to a binary")
    parser.add_argument('--riscv-dv-bin', help="The riscv-dv compiled binary", required=True)
    parser.add_argument('--config', help="Path to the config JSON object", required=True)
    parser.add_argument('--out-dir', help="Where the generated files should be placed", required=True)
    parser.add_argument('--out-prefix', help="Prefix for the generated files (.S, .bin, .elf)", required=True)
    args = parser.parse_args()

    riscv_dv_path = (Path.cwd() / "riscv-dv").resolve()
    riscv_dv_bin = Path(args.riscv_dv_bin).resolve()
    asm_file = Path(args.out_dir) / f"{args.out_prefix}"
    asm_file_out = Path(args.out_dir) / f"{args.out_prefix}_0.S"
    log_file = Path(args.out_dir) / f"{args.out_prefix}.log"

    # Generate asm file
    (cmd, envvars) = riscv_dv_cmd(generator_bin=riscv_dv_bin,
                                  config=RiscvDvConfig.parse_raw(Path(args.config).read_text()),
                                  out_asm_file=asm_file)
    try:
        stdout, stderr = run_cmd(cmd, envvars, timeout=30)
        log_file.resolve().write_text(stdout)
    except TimeoutExpired:
        print("ERROR: Generating asm from riscv-dv timed out!")
        sys.exit(1)

    # Generate elf
    (cmd, envvars) = gcc_cmd(asm_file_out, riscv_dv_path, f"{args.out_prefix}.elf")
    stdout, stderr = run_cmd(cmd, envvars, timeout=3)

    # Run elf with spike and measure expected instruction count or expected timeout
