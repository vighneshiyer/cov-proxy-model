import argparse
from pathlib import Path

from modeling.commands import run_cmd


def main():
    parser = argparse.ArgumentParser(prog="generate_elves",
                                     description="Generate asm, compile, and run spike for an entire config folder")
    parser.add_argument('--riscv-dv-bin', help="The riscv-dv compiled binary", required=True)
    parser.add_argument('--config-dir', help="Path to a directory of config JSON objects", required=True)
    args = parser.parse_args()

    riscv_dv_path = (Path.cwd() / "riscv-dv").resolve()
    riscv_dv_bin = Path(args.riscv_dv_bin).resolve()

    config_dir = Path(args.config_dir)
    for config_id in config_dir.iterdir():
        assert config_id.is_dir()
        for config_seed in config_id.glob("*.json"):
            cmd = ["generate_elf", "--riscv-dv-bin", str(riscv_dv_bin), "--config", config_seed.resolve(),
                   "--out-dir", str(config_id), "--out-prefix", config_seed.name.split('.')[0]]
            stdout, stderr, timeout = run_cmd(cmd, {}, timeout=None, check_return_code=False)  # failures are handled later
