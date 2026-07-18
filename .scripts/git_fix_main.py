import subprocess
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
print('repo', repo)

def run(cmd):
    print('>>>', ' '.join(cmd))
    proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    print('stdout:')
    print(proc.stdout)
    print('stderr:')
    print(proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f'Command failed: {cmd} returncode={proc.returncode}')
    return proc.stdout.strip()

print('HEAD file content:')
print((repo / '.git' / 'HEAD').read_text())
print('main hash:')
print((repo / '.git' / 'refs' / 'heads' / 'main').read_text())
fix_ref = repo / '.git' / 'refs' / 'heads' / 'fix' / 'update-workflow-tele-session'
print('fix hash:')
print(fix_ref.read_text())

print('git status -sb:')
run(['git', 'status', '-sb'])
print('switching to main...')
run(['git', 'switch', 'main'])
print('merging fix branch...')
run(['git', 'merge', '--no-ff', 'fix/update-workflow-tele-session', '-m', 'chore: merge fix/update-workflow-tele-session into main'])
print('pushing main...')
run(['git', 'push', 'origin', 'main'])
print('done')
print('final HEAD:')
print((repo / '.git' / 'HEAD').read_text())
print('final main hash:')
print((repo / '.git' / 'refs' / 'heads' / 'main').read_text())
