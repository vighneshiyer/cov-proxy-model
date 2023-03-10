import argparse
from pathlib import Path
from joblib import delayed, Parallel

from modeling.commands import run_cmd


def generate_elves(riscv_dv_bin, config_dir):
    riscv_dv_bin = Path(riscv_dv_bin).resolve()

    config_dir = Path(config_dir)
    programs = []
    for config_id in config_dir.iterdir():
        assert config_id.is_dir()
        for config_seed in config_id.glob("*.json"):
            programs.append(delayed(call_generate_elf)(riscv_dv_bin, config_id, config_seed))
    Parallel(n_jobs=24, prefer="threads")(programs)

def main():
    parser = argparse.ArgumentParser(prog="generate_elves",
                                     description="Generate asm, compile, and run spike for an entire config folder")
    parser.add_argument('--riscv-dv-bin', help="The riscv-dv compiled binary", required=True)
    parser.add_argument('--config-dir', help="Path to a directory of config JSON objects", required=True)
    args = parser.parse_args()

    generate_elves(args.riscv_dv_bin, args.config_dir)


def call_generate_elf(riscv_dv_bin: Path, config_id: Path, config_seed: Path) -> None:
    cmd = ["python3", "scripts/generate_elf.py", "--riscv-dv-bin", str(riscv_dv_bin), "--config", config_seed.resolve(),
           "--out-dir", str(config_id), "--out-prefix", config_seed.name.split('.')[0]]
    # If the spike status file already exists, skip this one
    if (config_seed.parent / config_seed.name.replace(".json", ".spike.status")).resolve().exists():
        return
    stdout, stderr, timeout = run_cmd(cmd, {}, timeout=None, check_return_code=False)  # failures are handled later

if __name__ == "__main__":
    main()