#  Original code under MIT License
#
#  Copyright (c) 2026 Oleksii Sylichenko
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import shutil
import subprocess
from pathlib import Path

THIS: Path = Path(__file__).parent

SPEC_FILE_NAME: Path = THIS / 'app.spec'
BUILD_PATH = THIS / '../build'
DIST_PATH = THIS / '../dist'


def make_exe(build_path: Path = BUILD_PATH, dist_path: Path = DIST_PATH) -> None:
    subprocess.run([
        'pyinstaller',
        '--clean',  # Clean PyInstaller cache and remove temporary files before building.
        '--workpath=' + str(build_path),
        # Where to put all the temporary work files, .log, .pyz and etc. (default: ./build)
        '--distpath=' + str(dist_path),  # Where to put the bundled app (default: ./dist)
        str(SPEC_FILE_NAME)
    ])


def remove_if_present(dir_path: Path):
    if dir_path.exists():
        shutil.rmtree(dir_path)


def clean():
    remove_if_present(BUILD_PATH)
    remove_if_present(DIST_PATH)


def make_output_dirs():
    BUILD_PATH.mkdir()
    DIST_PATH.mkdir()


if __name__ == '__main__':
    clean()
    make_output_dirs()
    make_exe()
