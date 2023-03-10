import argparse
from pathlib import Path
from subprocess import TimeoutExpired
import sys

from modeling.commands import run_cmd, riscv_dv_cmd, gcc_cmd, spike_cmd
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
    gen_log_file = Path(args.out_dir) / f"{args.out_prefix}.gen.log"
    spike_log_file = Path(args.out_dir) / f"{args.out_prefix}.spike.log"

    # Generate asm file
    (cmd, envvars) = riscv_dv_cmd(generator_bin=riscv_dv_bin,
                                  config=RiscvDvConfig.parse_raw(Path(args.config).read_text()),
                                  out_asm_file=asm_file)

    stdout, stderr, timeout = run_cmd(cmd, envvars, timeout=30)
    gen_log_file.resolve().write_text(stdout)
    if timeout:
        print("ERROR: Generating asm from riscv-dv timed out!")
        sys.exit(1)

    # Generate elf
    (cmd, envvars) = gcc_cmd(asm_file_out, riscv_dv_path, f"{args.out_prefix}.elf")
    stdout, stderr, timeout = run_cmd(cmd, envvars, timeout=3)
    assert timeout is False

    # Run elf with spike and measure expected instruction count or expected timeout
    (cmd, envvars) = spike_cmd(Path(args.out_dir) / f"{args.out_prefix}.elf")
    stdout, stderr, timeout = run_cmd(cmd, envvars, timeout=2)  # more than 2 seconds of spike runtime would be absurd
    spike_log_file.write_text(stderr)

    spike_status_file = (Path(args.out_dir) / f"{args.out_prefix}.spike.status")
    if timeout:
        spike_status_file.write_text("TIMEOUT")
    else:
        spike_status_file.write_text(str(len(stderr.split('\n'))))

if __name__ == "__main__":
    main()