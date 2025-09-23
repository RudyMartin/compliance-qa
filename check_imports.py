import os
import re
from pathlib import Path

# Standard library modules to exclude
STDLIB = {
    'abc', 'argparse', 'ast', 'asyncio', 'base64', 'builtins', 'collections',
    'concurrent', 'contextlib', 'copy', 'dataclasses', 'datetime', 'enum',
    'functools', 'glob', 'hashlib', 'importlib', 'inspect', 'io', 'json',
    'logging', 'math', 'os', 'pathlib', 'pickle', 'platform', 're', 'shutil',
    'socket', 'sqlite3', 'string', 'subprocess', 'sys', 'tempfile', 'textwrap',
    'threading', 'time', 'traceback', 'typing', 'unittest', 'urllib', 'uuid',
    'warnings', 'weakref', 'zipfile', 'cmath', 'html', 'http', 'multiprocessing',
    'random', 'secrets', 'statistics', 'struct', 'types'
}

# Project internal modules to exclude  
INTERNAL = {
    'common', 'domain', 'infrastructure', 'adapters', 'portals', 'packages',
    'tlm', 'tidyllm', 'tidyllm_sentence', 'config', 'application', 'api'
}

third_party = set()

for py_file in Path('.').rglob('*.py'):
    if 'test' in str(py_file) or 'functional' in str(py_file):
        continue
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find imports
            imports = re.findall(r'^(?:from|import)\s+([a-z_][a-z0-9_]*)', content, re.MULTILINE)
            for imp in imports:
                base_module = imp.split('.')[0]
                if base_module not in STDLIB and base_module not in INTERNAL:
                    third_party.add(base_module)
    except:
        pass

print("Third-party packages found:")
for pkg in sorted(third_party):
    print(f"  {pkg}")
