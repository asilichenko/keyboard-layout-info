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

import threading
import time
import tkinter as tk
from tkinter import ttk

from keyboard_layout_info import (
    KeyboardLayout,
    KlidResolver,
    LayoutInfo,
    LayoutInfoUtil
)


class App:
    APP_NAME = "Keyboard layout info"

    def __init__(self, klid_resolver: KlidResolver, keyboard_layout: KeyboardLayout, layout_util: LayoutInfoUtil):
        self.klid_resolver = klid_resolver

        self.keyboard_layout = keyboard_layout
        self.available_layouts = keyboard_layout.get_available()
        self.layout_util = layout_util

        self.root = tk.Tk()

        # StringVar для полів поточної розкладки
        self.var_name = tk.StringVar()

        self.var_hkl = tk.StringVar()
        self.var_klid = tk.StringVar()

        self.var_hkl_locale = tk.StringVar()
        self.var_klid_locale = tk.StringVar()

        self.var_hkl_country_code = tk.StringVar()
        self.var_klid_country_code = tk.StringVar()

        self.var_hkl_country_name = tk.StringVar()
        self.var_klid_country_name = tk.StringVar()

        self.var_hkl_scripts = tk.StringVar()
        self.var_klid_scripts = tk.StringVar()

    def _build_ui(self):
        self.root.title(self.APP_NAME)
        self.root.geometry("800x600")
        self._setup_styles()

        # ── Current layout ──────────────────────────────────────────
        current_frame = tk.LabelFrame(self.root, text="Current layout", padx=8, pady=8)
        current_frame.pack(fill="x", padx=10, pady=(10, 5))

        def add_row(parent, row_idx, label_text, var_left, var_right):
            tk.Label(parent, text=label_text, anchor="w", width=14).grid(
                row=row_idx, column=0, sticky="w", padx=(0, 8), pady=2
            )
            ttk.Entry(parent, textvariable=var_left, state="readonly", width=30).grid(
                row=row_idx, column=1, sticky="ew", padx=(0, 4), pady=2
            )
            ttk.Entry(parent, textvariable=var_right, state="readonly", width=30).grid(
                row=row_idx, column=2, sticky="ew", pady=2
            )

        # Рядок 0 — заголовки колонок
        tk.Label(current_frame, text="", width=14).grid(row=0, column=0)
        tk.Label(current_frame, text="HKL", anchor="w").grid(row=0, column=1, sticky="w", padx=(0, 4))
        tk.Label(current_frame, text="KLID", anchor="w").grid(row=0, column=2, sticky="w")

        # Рядок 1 — Name
        tk.Label(current_frame, text="Name", anchor="w", width=14).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=2
        )
        ttk.Entry(current_frame, textvariable=self.var_name, state="readonly").grid(
            row=1, column=1, columnspan=2, sticky="ew", pady=2
        )

        # Рядок 2 — ID (HKL / KLID)
        add_row(current_frame, 2, "ID", self.var_hkl, self.var_klid)
        add_row(current_frame, 3, "Locale", self.var_hkl_locale, self.var_klid_locale)
        add_row(current_frame, 4, "Country code", self.var_hkl_country_code, self.var_klid_country_code)
        add_row(current_frame, 5, "Country", self.var_hkl_country_name, self.var_klid_country_name)

        current_frame.grid_columnconfigure(1, weight=1)
        current_frame.grid_columnconfigure(2, weight=1)

        # ── Layout list ─────────────────────────────────────────────
        list_frame = tk.LabelFrame(self.root, text="Layout list", padx=8, pady=8)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.layout_table = self._add_table(list_frame)
        # noinspection PyTypeChecker
        self.layout_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _update_current(self, row: LayoutInfo):
        self.var_name.set(row.layout_name)

        self.var_hkl.set(row.hkl)
        self.var_klid.set(row.klid)

        self.var_hkl_locale.set(row.hkl_locale or "")
        self.var_klid_locale.set(row.klid_locale or "")

        self.var_hkl_country_code.set(row.hkl_country_code or "")
        self.var_klid_country_code.set(row.klid_country_code or "")

        self.var_hkl_country_name.set(row.hkl_country_name or "")
        self.var_klid_country_name.set(row.klid_country_name or "")

        self.var_hkl_scripts.set(row.hkl_scripts or "")
        self.var_klid_scripts.set(row.klid_scripts or "")

    @staticmethod
    def _setup_styles():
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading",
                        background="#d3e3fd",
                        foreground="black",
                        font=("Segoe UI", 9),
                        relief="flat",
                        )
        style.map("Treeview.Heading",
                  background=[("active", "#3a3a3a")],
                  foreground=[("active", "white")],
                  )

    @staticmethod
    def _add_table(parent: tk.Widget) -> ttk.Treeview:
        columns = ("ID", "Locale", "Scripts", "Country code", "Country")
        column_widths = {
            "ID": 20,
            "Locale": 20,
            "Scripts": 20,
            "Country code": 20,
            "Country": 150,
        }

        tree = ttk.Treeview(
            parent,
            columns=columns,
            show="tree headings",
        )

        # noinspection PyTypeChecker
        v_scrollbar = ttk.Scrollbar(tree, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=v_scrollbar.set)
        # noinspection PyTypeChecker
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree.column("#0", width=180, stretch=False)  # колонка назви розкладки
        tree.heading("#0", text="Layout")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 100), anchor="center")

        return tree

    def _update_layout_list(self, rows: list[LayoutInfo]):
        tree = self.layout_table

        # Будуємо індекс: layout_name → iid кореневого вузла
        existing: dict[str, str] = {}
        for iid in tree.get_children():
            name = tree.item(iid, "text")
            existing[name] = iid

        new_names = {row.layout_name for row in rows}

        # Видаляємо відсутні розкладки
        for name, iid in existing.items():
            if name not in new_names:
                tree.delete(iid)

        for row in rows:
            if row.layout_name in existing:
                root_id = existing[row.layout_name]
                children = tree.get_children(root_id)
                if len(children) == 2:
                    tree.item(children[0], text="HKL", values=(
                        row.hkl,
                        row.hkl_locale or "",
                        row.hkl_scripts or "",
                        row.hkl_country_code or "",
                        row.hkl_country_name or ""
                    ))
                    tree.item(children[1], text="KLID", values=(
                        row.klid,
                        row.klid_locale or "",
                        row.klid_scripts or "",
                        row.klid_country_code or "",
                        row.klid_country_name or ""
                    ))
            else:
                # noinspection PyTypeChecker
                root_id = tree.insert("", tk.END, text=row.layout_name)  # ← text= для #0
                # noinspection PyTypeChecker
                tree.insert(root_id, tk.END, text="HKL", values=(
                    row.hkl,
                    row.hkl_locale or "",
                    row.hkl_scripts or "",
                    row.hkl_country_code or "",
                    row.hkl_country_name or ""
                ))
                # noinspection PyTypeChecker
                tree.insert(root_id, tk.END, text="KLID", values=(
                    row.klid,
                    row.klid_locale or "",
                    row.klid_scripts or "",
                    row.klid_country_code or "",
                    row.klid_country_name or ""
                ))
                tree.item(root_id, open=True)

    def _loop(self):
        active_hkl_old = None
        while True:
            try:
                # Поточна активна розкладка
                active_hkl = self.keyboard_layout.get_active()
                if active_hkl != active_hkl_old:
                    active_hkl_old = active_hkl

                    active_row: LayoutInfo = self.layout_util.collect_info(active_hkl)
                    self.root.after(0, self._update_current, active_row)

                # Список усіх встановлених розкладок
                all_hkls = self.keyboard_layout.get_installed()
                all_rows = [self.layout_util.collect_info(hkl) for hkl in all_hkls]
                self.root.after(0, self._update_layout_list, all_rows)

            except Exception as e:
                print(f"Error: {e}")

            time.sleep(10)

    def run(self) -> None:
        self._build_ui()
        threading.Thread(target=self._loop, daemon=True).start()
        self.root.mainloop()


def run():
    keyboard_layout = KeyboardLayout()
    klid_resolver = KlidResolver()
    layout_util = LayoutInfoUtil(klid_resolver=klid_resolver, available_layouts=keyboard_layout.get_available())
    App(
        klid_resolver=klid_resolver,
        keyboard_layout=keyboard_layout,
        layout_util=layout_util
    ).run()


if __name__ == '__main__':
    run()
