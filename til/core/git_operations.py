import subprocess
import sys

def save_to_git(base_dir: str, commit_message: str):
    """Save changes to git."""
    print(f"📦 Git 저장 중: '{commit_message}'")

    cmds = [
        ["git", "add", "."],
        ["git", "commit", "-m", commit_message],
        ["git", "push", "origin", "main"]
    ]

    for cmd in cmds:
        result = subprocess.run(cmd, cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"❌ 실패: {' '.join(cmd)}")
            print(result.stderr.strip())
            sys.exit(1)
        else:
            print(f"✅ 완료: {' '.join(cmd)}")
