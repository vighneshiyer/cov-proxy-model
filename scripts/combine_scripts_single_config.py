from pathlib import Path
import argparse

from modeling.commands import run_cmd
from generate_elf import generate_elf
from run_rtl_sim import run_rtl_sim
from parse_coverages import parse_and_write_file

def combine_scripts_single_config(config_dir, config_num, config_seed, riscv_dv_bin, rtl_sim_bin, out_dir):
    json_dir = (config_dir / config_num / f"{config_seed}.json").resolve()
    generate_elf(riscv_dv_bin, json_dir, (config_dir / config_num).resolve(), config_seed)
    elf = (config_dir / config_num / f"{config_seed}.elf").resolve()
    spike_runtime = Path(elf.parent / f"{config_seed}.spike.status").read_text()
    log_file = Path(elf.parent / f"{config_seed}.sim.log")
    cov_file = Path(elf.parent / f"{config_seed}.cov.dat")

    if spike_runtime == "TIMEOUT":
        max_cycles = 300000
    else:
        max_cycles = int(spike_runtime) * 20

    run_rtl_sim(rtl_sim_bin, elf, max_cycles, log_file.resolve(), cov_file.resolve())

    if cov_file.exists():
        parse_and_write_file(config_dir, config_num, config_seed, out_dir)

def call_combine_scripts_single_config(config_dir, config_num, config_seed, riscv_dv_bin, rtl_sim_bin, out_dir):
    cmd = [
        "python3",
        "scripts/combine_scripts_single_config.py",
        "--config-dir", str(config_dir),
        "--config-num", str(config_num),
        "--config-seed", str(config_seed),
        "--riscv-dv-bin", str(riscv_dv_bin),
        "--rtl-sim-bin", str(rtl_sim_bin),
        "--out-dir", str(out_dir),
    ]
    stdout, stderr, timeout = run_cmd(cmd, {}, timeout=None, check_return_code=False)

def main():
    parser = argparse.ArgumentParser(prog="run_all_rtl_sims",
                                     description="Run RTL sims with coverage collection for an entire config folder")
    parser.add_argument('--config-dir', help="Path to a directory of coverage files", required=True)
    parser.add_argument('--config-num', help="Config number (under config-dir)", required=True)
    parser.add_argument('--config-seed', help="Seed number (under config-dir/config-num)", required=True)
    parser.add_argument('--riscv-dv-bin', help="The riscv-dv compiled binary", required=True)
    parser.add_argument('--rtl-sim-bin', help="The compiled Rocket-Chip rv32imc Verilator simulation binary", required=True)
    parser.add_argument('--out-dir', help="Where the generated files should be placed", required=True)
    args = parser.parse_args()

    if not Path(args.out_dir).exists():
        Path(args.out_dir).mkdir()
    
    combine_scripts_single_config(
        Path(args.config_dir),
        args.config_num,
        args.config_seed,
        Path(args.riscv_dv_bin),
        Path(args.rtl_sim_bin),
        Path(args.out_dir)
    )

if __name__ == "__main__":
    main()