import argparse
from pathlib import Path

from modeling.commands import run_cmd

def run_rtl_sim(rtl_sim_bin, elf, max_cycles, log_out, cov_out):
    cmd = [Path(rtl_sim_bin).resolve(), f"--cov={str(Path(cov_out).resolve())}",
           f"--max-cycles={max_cycles}", "--cycle-count", "--seed=1", Path(elf)]
    # assume about 1kHz simulation throughput (2x overhead for safety)
    stdout, stderr, timeout = run_cmd(cmd, envvars={}, timeout=max_cycles*(1/1e3)*2, check_return_code=False)
    Path(log_out).write_text(stdout + "\n" + stderr)

def main():
    parser = argparse.ArgumentParser(prog="run_rtl_sim",
                                     description="Run RTL simulation for a single ELF")
    parser.add_argument('--rtl-sim-bin', help="The compiled Rocket-Chip rv32imc Verilator simulation binary", required=True)
    parser.add_argument('--elf', help="The ELF to run", required=True)
    parser.add_argument('--max-cycles', type=int, help="Maximum number of simulation cycles before RTL sim is killed", required=True)
    parser.add_argument('--log-out', help="The output log file from running simulation", required=True)
    parser.add_argument('--cov-out', help="The output coverage file from running simulation", required=True)
    args = parser.parse_args()

    run_rtl_sim(args.rtl_sim_bin, args.elf, args.max_cycles, args.log_out, args.cov_out)

if __name__ == "__main__":
    main()
