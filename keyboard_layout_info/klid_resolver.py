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

import ctypes
import threading

from win32api import SendMessage, GetKeyboardLayoutName, GetKeyboardLayout
from win32con import WM_INPUTLANGCHANGEREQUEST
from win32gui import WNDCLASS, GetModuleHandle, RegisterClass, CreateWindow, PumpMessages

kernel32: ctypes.WinDLL = ctypes.windll.kernel32
user32: ctypes.WinDLL = ctypes.windll.user32


class KlidResolver:
    INPUTLANGCHANGE_SYSCHARSET: int = 0x0001

    _hwnd: int = 0  # HWND
    _ready: threading.Event = threading.Event()
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def _window_layout_processor_thread(cls) -> None:
        wc = WNDCLASS()
        # noinspection PyPropertyAccess
        wc.lpszClassName = cls.__name__
        # noinspection PyPropertyAccess
        wc.hInstance = GetModuleHandle(None)
        # noinspection PyTypeChecker
        class_atom: int = RegisterClass(wc)
        # noinspection PyTypeChecker
        cls._hwnd = CreateWindow(
            class_atom, wc.lpszClassName,
            0, 0, 0, 0, 0, 0, 0,
            wc.hInstance, None
        )
        if not cls._hwnd:
            raise RuntimeError(f"{cls.__name__}: failed to create hidden window")
        cls._ready.set()
        PumpMessages()

    @classmethod
    def _start(cls) -> None:
        if cls._ready.is_set():
            return
        cls.thread = threading.Thread(target=cls._window_layout_processor_thread, daemon=True, )
        cls.thread.start()
        cls._ready.wait()

    @classmethod
    def resolve(cls, hkl: int) -> str:
        with cls._lock:
            if not cls._hwnd:
                cls._start()

            current_hkl: int = GetKeyboardLayout(cls.thread.native_id or 0)
            if current_hkl == hkl:
                return GetKeyboardLayoutName().lower()


            # noinspection PyTypeChecker
            SendMessage(cls._hwnd, WM_INPUTLANGCHANGEREQUEST, cls.INPUTLANGCHANGE_SYSCHARSET, hkl)
            klid: str = GetKeyboardLayoutName()
            # noinspection PyTypeChecker
            SendMessage(cls._hwnd, WM_INPUTLANGCHANGEREQUEST, cls.INPUTLANGCHANGE_SYSCHARSET, current_hkl)
            return klid.lower()


def main() -> None:
    from win32api import GetKeyboardLayoutList

    for hkl in GetKeyboardLayoutList():
        klid = KlidResolver.resolve(hkl)
        print(f'{hkl = :08x} ({hkl & 0xFFFFFFFF:08x}) • {klid = }')


if __name__ == '__main__':
    main()
