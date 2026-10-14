"""Find every internal import between tracked .ts/.tsx files (relative, @/ alias, @digital-bank/shared)."""
import re, os, subprocess, sys


def find_edges(root):
    files = [f for f in subprocess.check_output(['git', '-C', root, 'ls-files']).decode().split('\n')
             if re.search(r'\.(ts|tsx)$', f)]
    fs = set(files)

    def resolve(src, spec):
        if spec == '@digital-bank/shared':
            return 'packages/shared/src/index.ts'
        if spec.startswith('@/'):
            base = os.path.join('app', spec[2:])
        elif spec.startswith('.'):
            base = os.path.normpath(os.path.join(os.path.dirname(src), spec))
        else:
            return None
        for ext in ['', '.ts', '.tsx', '/index.ts']:
            if base + ext in fs:
                return base + ext
        raise SystemExit(f'{src}: could not resolve import {spec!r}')

    edges = []
    for f in files:
        s = open(os.path.join(root, f)).read()
        for m in re.finditer(r"""(?:import|export)\s[^;]*?from\s+['"]([^'"]+)['"]""", s, re.S):
            t = resolve(f, m.group(1))
            if t:
                edges.append((f, t))
    return edges


if __name__ == '__main__':
    for a, b in find_edges(sys.argv[1] if len(sys.argv) > 1 else '.'):
        print(f'{a}  ->  {b}')
