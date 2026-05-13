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

import winreg

from win32api import GetKeyboardLayoutList, GetKeyboardLayout
from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId


class KeyboardLayout:

    @staticmethod
    def get_active() -> int:
        foreground_window_handle: int = GetForegroundWindow()
        thread_id: int = GetWindowThreadProcessId(foreground_window_handle)[0]
        return GetKeyboardLayout(thread_id)

    @staticmethod
    def get_installed() -> tuple[int, ...]:
        return GetKeyboardLayoutList()

    @staticmethod
    def get_available() -> dict[str, str]:
        key_path: str = r"SYSTEM\CurrentControlSet\Control\Keyboard Layouts"
        result = {}
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            i = 0
            while True:
                try:
                    klid: str = winreg.EnumKey(key, i).lower()
                    with winreg.OpenKey(key, klid) as subkey:
                        try:
                            result[klid] = winreg.QueryValueEx(subkey, "Layout Text")[0]
                        except FileNotFoundError:
                            pass
                    i += 1
                except OSError:
                    break
        return result


def main():
    def sep():
        print(f'+{"-" * 60}')

    sep()
    print("| Available (KLID)")
    sep()

    for i, (klid, name) in enumerate(KeyboardLayout.get_available().items()):
        print(f'| {i:3} | {klid} | {name}')

    sep()
    print("| Installed (HKL)")
    sep()

    for i, layout in enumerate(KeyboardLayout.get_installed()):
        print(f'| {i:2} | {layout:08x} | {layout & 0xFFFFFFFF:08x}')

    sep()

    print(f'| Active layout: {KeyboardLayout.get_active() :08x}')

    sep()


# def main_scripts():


if __name__ == '__main__':
    main()
