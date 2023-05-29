from typing import List, Optional, Tuple, Dict
import subprocess
import signal
import logging
import shutil
from pathlib import Path
import os
import sys
from subprocess import TimeoutExpired

from modeling.riscv_dv import RiscvDvConfig

envvars_t = Dict[str, str]
cmd_t = Tuple[List[str], envvars_t]
isa_str = "rv32imc"


# Return stdout, stderr, and timeout status (True = timed out, False = finished)
def run_cmd(cmd: List[str], envvars: envvars_t = {},
            timeout: Optional[int] = None, check_return_code: bool = True) -> Tuple[str, str, bool]:
    print(f"Running command with args {cmd} and envvars {envvars}")

    env = os.environ.copy()
    for key, value in envvars.items():
        env[key] = value
        # env["PATH"] = "/usr/sbin:/sbin:" + my_env["PATH"]

    try:
        proc = subprocess.run(cmd, env=env, timeout=timeout, text=True, capture_output=True)
    except TimeoutExpired as e:
        print("TIMEOUT", e)
        if e.stdout:
            sout = e.stdout.decode("utf-8")
        else:
            sout = ""
        if e.stderr:
            serr = e.stderr.decode("utf-8")
        else:
            serr = ""
        return sout, serr, True

    if check_return_code:
        if proc.returncode != 0:
            print("Command terminated with non-zero return code")
            print(proc.stdout)
            print(proc.stderr)
        proc.check_returncode()
    return proc.stdout, proc.stderr, False

    # proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # try:
    #     while True:
    #         if proc.stdout:
    #             line = proc.stdout.readline()
    #             if line and print_stdout:
    #                 print(line, end='')
    #             else:
    #                 break
    #         if proc.stderr:
    #             line = proc.stderr.readline()
    #             if line and print_stderr:
    #                 print(line, end='')
    #             else:
    #                 break
    #     if timeout:
    #         proc.wait(timeout=timeout)
    #     else:
    #         proc.wait()
    # except KeyboardInterrupt:
    #     proc.send_signal(signal.SIGINT)
    #     raise
    # except subprocess.TimeoutExpired:
    #     proc.kill()
    #     raise
    # if proc.returncode != 0 and check_return_code:
    #     logging.debug(f"Command failed with return code {proc.returncode}")
    #     raise subprocess.CalledProcessError(proc.returncode, cmd)
    # return proc.stdout.read(), proc.stderr.read()


# Returns the command as a list of pieces and a dictionary indicating the environment variables to set
def vcs_build_cmd(riscv_dv_path: Path, working_dir: Path, out: Path, cov: bool = False) -> cmd_t:
    assert cov is False  # haven't handled generator coverage collection yet
    vcs_opts = [
        '-full64',
        '-sverilog',
        '-ntb_opts', 'uvm-1.2',
        '-lca',
        '+define+UVM_REGEX_NO_DPI',
        '-timescale=1ns/10ps',
        f"+incdir+{riscv_dv_path}/target/{isa_str}",
        f"+incdir+{riscv_dv_path}/user_extension",
        "-f", f"{riscv_dv_path}/files.f",
        "-l", f"{str(working_dir)}/compile.log",
        "-LDFLAGS", '-Wl,--no-as-needed',
        "-CFLAGS", '--std=c99 -fno-extended-identifiers',
        f"-Mdir={str(working_dir)}/vcs_simv.csrc",
        "-o", f"{str(out)}"
    ]
    vcs_path = shutil.which('vcs')
    assert vcs_path is not None
    final_cmd = [vcs_path] + vcs_opts
    return final_cmd, {'RISCV_DV_ROOT': str(riscv_dv_path)}


def riscv_dv_cmd(generator_bin: Path, config: RiscvDvConfig, out_asm_file: Path) -> cmd_t:
    # -cm_dir <out>/test.vdb -cm_log /dev/null -cm_name test_<seed>_<test_id>
    plusargs = [f"+{key}={value}" for key, value in config.plusarg_config.items()]
    seed = f"+ntb_random_seed={config.seed}"
    gen_test = "riscv_instr_base_test"
    uvm_testname = f"+UVM_TESTNAME={gen_test}"
    start_idx = "+start_idx=0"
    asm_file_name = f"+asm_file_name={str(out_asm_file.resolve())}"

    cmd = [generator_bin.resolve(), "+vcs+lic+wait"] + plusargs + [seed, uvm_testname, start_idx, asm_file_name]
    return cmd, {}


def gcc_cmd(asm_file: Path, riscv_dv_path: Path, elf_name: str) -> cmd_t:
    gcc = os.environ['RISCV'] + "/bin/riscv64-unknown-elf-gcc"
    opts = [
        "-static",
        "-mcmodel=medany",
        "-fvisibility=hidden",
        "-nostdlib",
        "-nostartfiles",
        f"-march={isa_str}",
        f"-mabi=ilp32",
        f"-I{riscv_dv_path}/user_extension",
        f"-T{riscv_dv_path}/scripts/link.ld"
    ]
    return [gcc] + opts + [str(asm_file.resolve())] + ["-o", str(asm_file.parent / elf_name)], {}


def spike_cmd(elf_file: Path) -> cmd_t:
    cmd = [os.environ['RISCV'] + "/bin/spike", "--log-commits", f"--isa={isa_str}", "-l", str(elf_file.resolve())]
    return cmd, {}
