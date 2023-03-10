import argparse
from pathlib import Path
from joblib import delayed, Parallel

from modeling.commands import run_cmd

def run_all_rtl_sims(rtl_sim_bin, config_dir):
    config_dir = Path(config_dir)
    programs = []
    for config_id in config_dir.iterdir():
        assert config_id.is_dir()
        for elf in config_id.glob("*.elf"):
            programs.append(delayed(call_run_rtl_sim)(Path(rtl_sim_bin), elf))
    Parallel(n_jobs=28, prefer="threads")(programs)

def main():
    parser = argparse.ArgumentParser(prog="run_all_rtl_sims",
                                     description="Run RTL sims with coverage collection for an entire config folder")
    parser.add_argument('--rtl-sim-bin', help="The compiled Rocket-Chip rv32imc Verilator simulation binary", required=True)
    parser.add_argument('--config-dir', help="Path to a directory of config JSON objects", required=True)
    args = parser.parse_args()

    run_all_rtl_sims(args.rtl_sim_bin, args.config_dir)


def call_run_rtl_sim(rtl_sim_bin: Path, elf: Path) -> None:
    idx = int(elf.name.replace(".elf", ""))  # this is the seed idx
    assert idx >= 0
    spike_runtime = Path(elf.parent / f"{idx}.spike.status").read_text()
    log_file = Path(elf.parent / f"{idx}.sim.log")
    cov_file = Path(elf.parent / f"{idx}.cov.dat")

    if spike_runtime == "TIMEOUT":
        max_cycles = str(300000)
    else:
        max_cycles = str(int(spike_runtime) * 20)

    cmd = ["python3", "scripts/run_rtl_sim.py", "--rtl-sim-bin", str(rtl_sim_bin), "--elf", str(elf), "--max-cycles", max_cycles,
           "--log-out", log_file.resolve(), "--cov-out", cov_file.resolve()]
    # If the log and coverage files already exist, skip running this simulation
    if log_file.exists() and cov_file.exists():
        return
    # timeouts and logging are handled in the script itself
    stdout, stderr, timeout = run_cmd(cmd, {}, timeout=None, check_return_code=False)

if __name__ == "__main__":
    main()
