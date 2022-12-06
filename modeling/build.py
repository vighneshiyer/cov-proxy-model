from typing import List, Optional, Tuple, Dict
import subprocess
import signal
import logging
import shutil
from pathlib import Path
import os

envvars_t = Dict[str, str]


def run_cmd(cmd: List[str], envvars: envvars_t = {}, timeout: Optional[int] = None, print_stdout: bool = False,
            print_stderr: bool = True, check_return_code: bool = True) -> Tuple[str, str]:
    logging.debug(f"Running command with args {cmd} and envvars {envvars}")

    env = os.environ.copy()
    for key, value in envvars.items():
        env[key] = value
        # env["PATH"] = "/usr/sbin:/sbin:" + my_env["PATH"]

    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        while True:
            if proc.stdout and print_stdout:
                line = proc.stdout.readline()
                if line:
                    print(line, end='')
                else:
                    break
        while True:
            if proc.stderr and print_stderr:
                line = proc.stderr.readline()
                if line:
                    print(line, end='')
                else:
                    break
        if timeout:
            proc.wait(timeout=timeout)
        else:
            proc.wait()
    except KeyboardInterrupt:
        proc.send_signal(signal.SIGINT)
        raise
    except subprocess.TimeoutExpired:
        proc.kill()
        raise
    if proc.returncode != 0 and check_return_code:
        logging.debug(f"Command failed with return code {proc.returncode}")
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    return proc.stdout.read(), proc.stderr.read()


# Returns the command as a list of pieces and a dictionary indicating the environment variables to set
def vcs_build_cmd(riscv_dv_path: Path, working_dir: Path, out: Path, cov: bool = False) -> Tuple[List[str], envvars_t]:
    assert cov is False  # haven't handled generator coverage collection yet
    vcs_opts = [
        '-full64',
        '-sverilog',
        '-ntb_opts', 'uvm-1.2',
        '-lca',
        '+define+UVM_REGEX_NO_DPI',
        '-timescale=1ns/10ps',
        f"+incdir+{riscv_dv_path}/target/rv64gc",
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
