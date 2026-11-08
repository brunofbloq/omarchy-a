"""The build imports none of orchard's Python: orchard's producers run as commands (orchard docs/distribution-contract.md).

Tests may import orchard; they test against it. The standalone tools/j71
research commands run in the pinned Orchard environment, outside the distro
build. Production code must not import that research namespace either.
"""
import ast
import os
from pathlib import Path
import unittest

PROJECT = Path(__file__).resolve().parents[1]


def python_files():
    excluded = {'tests', 'out', '.work', '.orchard', '.git'}
    for directory, children, files in os.walk(PROJECT):
        relative = Path(directory).relative_to(PROJECT)
        children[:] = sorted(name for name in children
                             if name != '__pycache__'
                             and not (relative == Path('.') and (name in excluded or name.startswith('.venv')))
                             and not (relative == Path('tools') and name == 'j71'))
        for name in sorted(files):
            path = Path(directory) / name
            if path.suffix == '.py':
                yield path
            elif not path.suffix:
                header = path.read_bytes()[:64]
                if header.startswith(b'#!') and b'python' in header:
                    yield path


class NoOrchardImports(unittest.TestCase):
    def test_no_build_file_imports_orchard(self):
        files = list(python_files())
        self.assertIn(PROJECT / 'tools/build.py', files)
        self.assertIn(PROJECT / 'desktop/build-labwc', files)
        for path in files:
            for node in ast.walk(ast.parse(path.read_text(), str(path))):
                names = ([alias.name for alias in node.names] if isinstance(node, ast.Import) else
                         [node.module or ''] if isinstance(node, ast.ImportFrom) and not node.level else [])
                for name in names:
                    with self.subTest(path=str(path.relative_to(PROJECT)), module=name):
                        self.assertNotEqual(name.split('.')[0], 'orchard')
                        self.assertFalse(name == 'tools.j71' or name.startswith('tools.j71.'))


if __name__ == '__main__':
    unittest.main()
