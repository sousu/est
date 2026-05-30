"""docker exec で estcmd を呼び出すユーティリティ"""
import subprocess
import sys

CONTAINER = "est"

def sh(*args, check=True, quiet=False):
    """コンテナ内で任意コマンドを実行"""
    cmd = ["docker", "exec", CONTAINER] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not quiet:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def estcmd(*args, stdin=None, check=True, quiet=False, on_line=None):
    cmd = ["docker", "exec", "-i", CONTAINER, "estcmd"] + list(args)
    if on_line is not None:
        return _estcmd_stream(cmd, stdin, check, on_line)
    result = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    if not quiet:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    elif result.stderr:
        # quiet時はestcmd ERRのみ表示
        errs = [l for l in result.stderr.splitlines() if "estcmd: ERR" in l]
        if errs:
            print("\n".join(errs), file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def _estcmd_stream(cmd, stdin, check, on_line):
    """出力を1行ずつ on_line に渡しながら実行 (進捗表示用)
    estcmd の INFO 進捗は stdout に出るため stderr も stdout へ統合する"""
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    if stdin is not None:
        proc.stdin.write(stdin)
    proc.stdin.close()
    errs = []
    for line in proc.stdout:
        on_line(line)
        if "estcmd: ERR" in line:
            errs.append(line.rstrip())
    proc.wait()
    if errs:
        print("\n" + "\n".join(errs), file=sys.stderr)
    if check and proc.returncode != 0:
        sys.exit(proc.returncode)
    return proc
