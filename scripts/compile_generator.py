import argparse
from pathlib import Path

from modeling.commands import vcs_build_cmd, run_cmd

def compile_generator(working_dir, out):
    riscv_dv_path = Path.cwd() / "riscv-dv"
    working_dir = Path(working_dir).resolve()
    working_dir.mkdir(exist_ok=True)
    bin_output = working_dir / out
    cmd, envvars = vcs_build_cmd(riscv_dv_path, working_dir, bin_output)
    run_cmd(cmd, envvars)

def main():
    parser = argparse.ArgumentParser(prog="compile_generator", description="Compile riscv-dv using VCS")
    parser.add_argument('--working-dir', help="Scratch directory used for VCS compilation", required=True)
    parser.add_argument('--out', help="Name of the compiled riscv-dv binary", required=True)
    args = parser.parse_args()
    compile_generator(args.working_dir, args.out)
    
if __name__ == "__main__":
    main()