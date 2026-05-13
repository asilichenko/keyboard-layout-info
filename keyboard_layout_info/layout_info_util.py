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

from keyboard_layout_info.klid_resolver import KlidResolver
from keyboard_layout_info.layout_info import LayoutInfo

kernel32: ctypes.WinDLL = ctypes.windll.kernel32


def make_lcid(layout_id: str | int) -> int | None:
    lang_id: int = (int(layout_id, 16) if isinstance(layout_id, str) else layout_id) & 0xFFFF
    return lang_id & 0xFFFFFFFF if 0x0c00 != lang_id else None


def lcid_to_locale_name(lcid: int) -> str | None:
    LOCALE_NAME_MAX_LENGTH = 85
    buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
    result: int = kernel32.LCIDToLocaleName(lcid, buffer, LOCALE_NAME_MAX_LENGTH, 0)
    return buffer.value if result > 0 else None


def get_locale_info_ex(locale_name: str | None, lc_type: int) -> str | None:
    if locale_name is None:
        return None

    buf_size: int = kernel32.GetLocaleInfoEx(locale_name, lc_type, None, 0)
    if buf_size == 0:
        return None
    buf = ctypes.create_unicode_buffer(buf_size)
    result_size: int = kernel32.GetLocaleInfoEx(locale_name, lc_type, buf, buf_size)
    return buf.value if result_size > 0 else None


def get_country_name(locale_name: str | None) -> str | None:
    LOCALE_SENGLISHCOUNTRYNAME: int = 0x1002
    return get_locale_info_ex(locale_name, LOCALE_SENGLISHCOUNTRYNAME)


def get_country_code(locale_name: str | None) -> str | None:
    LOCALE_SISO3166CTRYNAME = 0x005A
    return get_locale_info_ex(locale_name, LOCALE_SISO3166CTRYNAME)


def get_scripts(locale_name: str | None) -> str | None:
    LOCALE_SSCRIPTS = 0x0000006c  # Повертає скрипти BCP47, напр. "Latn", "Cyrl", "Arab"
    return get_locale_info_ex(locale_name, LOCALE_SSCRIPTS)


class LayoutInfoUtil:

    def __init__(self, klid_resolver: KlidResolver, available_layouts: dict[str, str]):
        self.klid_resolver = klid_resolver
        self.available_layouts = available_layouts

    def collect_info(self, hkl: int) -> LayoutInfo:
        klid = self.klid_resolver.resolve(hkl)
        layout_name = self.available_layouts.get(klid, f"Unknown ({klid})")

        hkl_lcid = make_lcid(hkl)
        klid_lcid = make_lcid(klid)

        hkl_locale = lcid_to_locale_name(hkl_lcid) if hkl_lcid is not None else None
        klid_locale = lcid_to_locale_name(klid_lcid) if klid_lcid is not None else None

        return LayoutInfo(
            layout_name=layout_name,
            hkl=f'{hkl:08x}',
            klid=klid,
            hkl_locale=hkl_locale or '-',
            klid_locale=klid_locale or '-',
            hkl_country_code=get_country_code(hkl_locale) or '-',
            klid_country_code=get_country_code(klid_locale) or '-',
            hkl_country_name=get_country_name(hkl_locale) or '-',
            klid_country_name=get_country_name(klid_locale) or '-',
            hkl_scripts=get_scripts(hkl_locale) or '-',
            klid_scripts=get_scripts(klid_locale) or '-',
        )
