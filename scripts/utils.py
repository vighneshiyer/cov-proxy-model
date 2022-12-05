import subprocess
import logging
import signal
from typing import List, Tuple, Optional

def run_cmd(cmd: List[str], timeout: Optional[int] = None, print_stdout: bool = False, print_stderr: bool = True, check_return_code: bool = True) -> Tuple[str, str]:
    print(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        while True:
            if proc.stdout:
                line = proc.stdout.readline()
                if line:
                    print(line, end='')
                else:
                    break
        while True:
            if proc.stderr:
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
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)
    return proc.stdout.read(), proc.stderr.read()
