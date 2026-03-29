#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scene (szken) kezelő GUI – Tkinter + Pillow

Funkciók:
- Legfrissebb kép miniatűr megjelenítése (és a legutóbbi 4 thumbnail csíkban)
- Képmappa fájljainak listázása
- Mappa mérete, fájlszám, meghajtó (disk) használat kijelzése
- 3 gomb: SCAN / CONNECT / SAVE (SCAN/CONNECT stub, SAVE működik másolással)

Szükséges: pip install pillow
"""

import os
import sys
import time
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit("Hiányzik a Pillow. Telepítsd: pip install pillow")


# ========= BEÁLLÍTÁSOK =========
IMAGES_DIR = r"./images"  # <-- Állítsd be a képmappát (pl. r"C:\scans" vagy "/home/user/scans")
REFRESH_MS = 1000         # frissítés időköze (ms)
RECENT_THUMB_COUNT = 4    # felül ennyi miniatűrt mutat
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
THUMB_SIZE = (120, 80)    # kis thumbnail méret (felül)
PREVIEW_SIZE = (420, 260) # nagyobb preview méret (bal felül)
# ==============================


@dataclass
class FileInfo:
    path: Path
    size: int
    mtime: float


def human_bytes(num: int) -> str:
    """Byte -> emberbarát méret"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.2f} {unit}"
        num /= 1024
    return f"{num:.2f} PB"


def list_images(folder: Path) -> list[FileInfo]:
    """Képfájlok listázása mtime szerint csökkenő sorrendben."""
    if not folder.exists() or not folder.is_dir():
        return []
    out = []
    for p in folder.iterdir():
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
            try:
                st = p.stat()
                out.append(FileInfo(path=p, size=st.st_size, mtime=st.st_mtime))
            except OSError:
                continue
    out.sort(key=lambda x: x.mtime, reverse=True)
    return out


def folder_size_bytes(folder: Path) -> int:
    """Mappa rekurzív mérete (byte)."""
    total = 0
    if not folder.exists() or not folder.is_dir():
        return 0
    for root, _, files in os.walk(folder):
        for fn in files:
            fp = Path(root) / fn
            try:
                total += fp.stat().st_size
            except OSError:
                pass
    return total


def safe_open_image(path: Path) -> Image.Image | None:
    """Kép megnyitása biztonságosan."""
    try:
        img = Image.open(path)
        img.load()
        return img
    except Exception:
        return None


class SceneManagerGUI(tk.Tk):
    def __init__(self, images_dir: Path):
        super().__init__()
        self.title("Scene Manager")
        self.geometry("900x560")
        self.minsize(860, 520)

        self.images_dir = images_dir
        self._last_snapshot_key = None

        # Tkinter PhotoImage referenciák tárolása (különben “eltűnnek”)
        self._thumb_refs: list[ImageTk.PhotoImage] = []
        self._preview_ref: ImageTk.PhotoImage | None = None

        self._build_ui()
        self._schedule_refresh(initial=True)

    def _build_ui(self):
        # ===== Fő rács =====
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # top thumbnails
        self.rowconfigure(1, weight=1)  # middle
        self.rowconfigure(2, weight=0)  # bottom buttons

        # ===== Top: thumbnail strip =====
        top = ttk.Frame(self, padding=(10, 10, 10, 5))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        self.thumb_strip = ttk.Frame(top)
        self.thumb_strip.grid(row=0, column=0, sticky="ew")
        for i in range(RECENT_THUMB_COUNT):
            self.thumb_strip.columnconfigure(i, weight=1)

        self.thumb_labels: list[ttk.Label] = []
        for i in range(RECENT_THUMB_COUNT):
            lbl = ttk.Label(self.thumb_strip, text="(nincs kép)", anchor="center", relief="ridge")
            lbl.grid(row=0, column=i, padx=6, sticky="ew")
            self.thumb_labels.append(lbl)

        # ===== Middle: left preview + info, right list =====
        mid = ttk.Frame(self, padding=(10, 5, 10, 5))
        mid.grid(row=1, column=0, sticky="nsew")
        mid.columnconfigure(0, weight=0)  # left
        mid.columnconfigure(1, weight=1)  # right
        mid.rowconfigure(0, weight=1)

        left = ttk.Frame(mid)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        left.rowconfigure(0, weight=0)
        left.rowconfigure(1, weight=0)
        left.rowconfigure(2, weight=1)

        # Preview (nagyobb miniatűr)
        preview_frame = ttk.LabelFrame(left, text="Legfrissebb scenelés", padding=8)
        preview_frame.grid(row=0, column=0, sticky="ew")
        self.preview_label = ttk.Label(preview_frame, text="Nincs találat", anchor="center", relief="sunken")
        self.preview_label.grid(row=0, column=0, sticky="ew")

        # Info panel
        info = ttk.LabelFrame(left, text="Mappa adatok", padding=8)
        info.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        info.columnconfigure(1, weight=1)

        ttk.Label(info, text="Mappa:").grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar(value=str(self.images_dir.resolve()))
        self.path_lbl = ttk.Label(info, textvariable=self.path_var, wraplength=360)
        self.path_lbl.grid(row=0, column=1, sticky="w")

        ttk.Label(info, text="Fájlok:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.count_var = tk.StringVar(value="0 db")
        ttk.Label(info, textvariable=self.count_var).grid(row=1, column=1, sticky="w", pady=(6, 0))

        ttk.Label(info, text="Mappa méret:").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.folder_size_var = tk.StringVar(value="0 B")
        ttk.Label(info, textvariable=self.folder_size_var).grid(row=2, column=1, sticky="w", pady=(6, 0))

        ttk.Label(info, text="Meghajtó:").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.disk_var = tk.StringVar(value="—")
        ttk.Label(info, textvariable=self.disk_var).grid(row=3, column=1, sticky="w", pady=(6, 0))

        ttk.Label(info, text="Utoljára frissítve:").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.updated_var = tk.StringVar(value="—")
        ttk.Label(info, textvariable=self.updated_var).grid(row=4, column=1, sticky="w", pady=(6, 0))

        # Folder picker
        pick_frame = ttk.Frame(left)
        pick_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(pick_frame, text="Képmappa kiválasztása…", command=self._pick_folder).grid(row=0, column=0, sticky="ew")

        # Right: file list
        right = ttk.LabelFrame(mid, text="Képek listája (név / méret / dátum)", padding=8)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        cols = ("name", "size", "mtime")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("name", text="Fájl")
        self.tree.heading("size", text="Méret")
        self.tree.heading("mtime", text="Módosítva")
        self.tree.column("name", width=420, anchor="w")
        self.tree.column("size", width=90, anchor="e")
        self.tree.column("mtime", width=160, anchor="w")

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_file)

        # ===== Bottom: buttons =====
        bottom = ttk.Frame(self, padding=(10, 5, 10, 10))
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)
        bottom.columnconfigure(2, weight=1)

        self.btn_scan = ttk.Button(bottom, text="SCAN", command=self._scan)
        self.btn_connect = ttk.Button(bottom, text="CONNECT", command=self._connect)
        self.btn_save = ttk.Button(bottom, text="SAVE", command=self._save)

        self.btn_scan.grid(row=0, column=0, sticky="ew", padx=6)
        self.btn_connect.grid(row=0, column=1, sticky="ew", padx=6)
        self.btn_save.grid(row=0, column=2, sticky="ew", padx=6)

    # ---------- Actions ----------
    def _pick_folder(self):
        chosen = filedialog.askdirectory(initialdir=str(self.images_dir), title="Válaszd ki a képmappát")
        if chosen:
            self.images_dir = Path(chosen)
            self.path_var.set(str(self.images_dir.resolve()))
            self._force_refresh()

    def _scan(self):
        # Itt kell majd bekötni a tényleges szkennelést (WIA/TWAIN/SANE / vendor tool).
        # Addig csak tájékoztató.
        messagebox.showinfo(
            "SCAN",
            "A SCAN gomb most csak helyőrző.\n\n"
            "Mondd meg, milyen operációs rendszer (Windows/Linux) és milyen szkenner API (WIA/TWAIN/SANE), "
            "és bekötöm ide a valódi szkennelést."
        )

    def _connect(self):
        # Tipikusan itt lenne eszközválasztó / beállítás (DPI, szín, mentési formátum, stb.)
        messagebox.showinfo(
            "CONNECT",
            "CONNECT: helyőrző beállító panel.\n\n"
            "Ha megírod a szkenner típusát és a kívánt beállításokat (DPI, szín, A4, stb.), "
            "készítek hozzá konfigurációs ablakot."
        )

    def _save(self):
        # A legfrissebb kép (vagy kijelölt) mentése/másolása másik helyre.
        selected = self._get_selected_path()
        if selected is None:
            newest = self._get_newest_image()
            if newest is None:
                messagebox.showwarning("SAVE", "Nincs menthető kép.")
                return
            selected = newest

        dest = filedialog.asksaveasfilename(
            title="Mentés másként",
            initialfile=selected.name,
            defaultextension=selected.suffix,
            filetypes=[
                ("Képek", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"),
                ("Minden fájl", "*.*"),
            ],
        )
        if not dest:
            return
        try:
            shutil.copy2(selected, dest)
            messagebox.showinfo("SAVE", f"Sikeres mentés:\n{dest}")
        except Exception as e:
            messagebox.showerror("SAVE", f"Nem sikerült menteni:\n{e}")

    # ---------- UI helpers ----------
    def _get_selected_path(self) -> Path | None:
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        values = self.tree.item(iid, "values")
        if not values:
            return None
        name = values[0]
        return self.images_dir / name

    def _on_select_file(self, _event=None):
        p = self._get_selected_path()
        if p and p.exists():
            self._set_preview_image(p)

    def _get_newest_image(self) -> Path | None:
        imgs = list_images(self.images_dir)
        return imgs[0].path if imgs else None

    def _snapshot_key(self, infos: list[FileInfo]) -> tuple:
        # gyors “változásdetektálás”: fájlnév+mtime+size top N elemre
        top = infos[:20]
        return tuple((x.path.name, int(x.mtime), x.size) for x in top)

    def _force_refresh(self):
        self._last_snapshot_key = None
        self._refresh()

    def _schedule_refresh(self, initial=False):
        if initial:
            self._refresh()
        self.after(REFRESH_MS, self._schedule_refresh)

    def _refresh(self):
        infos = list_images(self.images_dir)
        key = self._snapshot_key(infos)
        if key != self._last_snapshot_key:
            self._last_snapshot_key = key
            self._update_all(infos)

        # “Utoljára frissítve” mindig frissülhet
        self.updated_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _update_all(self, infos: list[FileInfo]):
        # Info számok
        self.count_var.set(f"{len(infos)} db")
        self.folder_size_var.set(human_bytes(folder_size_bytes(self.images_dir)))

        # Disk usage (a mappa meghajtóján)
        try:
            usage = shutil.disk_usage(self.images_dir)
            used = usage.used
            total = usage.total
            free = usage.free
            self.disk_var.set(f"Használt: {human_bytes(used)} / Össz: {human_bytes(total)} | Szabad: {human_bytes(free)}")
        except Exception:
            self.disk_var.set("—")

        # Tree frissítése
        for item in self.tree.get_children():
            self.tree.delete(item)

        for fi in infos:
            mtime_str = datetime.fromtimestamp(fi.mtime).strftime("%Y-%m-%d %H:%M:%S")
            self.tree.insert("", "end", values=(fi.path.name, human_bytes(fi.size), mtime_str))

        # Thumbnail strip frissítése (legutóbbi N)
        self._thumb_refs.clear()
        for i in range(RECENT_THUMB_COUNT):
            if i < len(infos):
                p = infos[i].path
                thumb = self._make_thumb(p, THUMB_SIZE)
                if thumb:
                    self._thumb_refs.append(thumb)
                    self.thumb_labels[i].configure(image=thumb, text="")
                else:
                    self.thumb_labels[i].configure(image="", text="(hibás kép)")
            else:
                self.thumb_labels[i].configure(image="", text="(nincs kép)")

        # Preview (legfrissebb)
        newest = infos[0].path if infos else None
        if newest:
            self._set_preview_image(newest)
        else:
            self.preview_label.configure(text="Nincs találat", image="")
            self._preview_ref = None

    def _make_thumb(self, path: Path, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
        img = safe_open_image(path)
        if img is None:
            return None
        # aránytartó miniatűr
        img = img.copy()
        img.thumbnail(size, Image.Resampling.LANCZOS)
        # Kis “keret” hatás: fehér háttérre középre
        canvas = Image.new("RGB", size, (245, 245, 245))
        x = (size[0] - img.size[0]) // 2
        y = (size[1] - img.size[1]) // 2
        if img.mode in ("RGBA", "LA"):
            canvas.paste(img, (x, y), img)
        else:
            canvas.paste(img, (x, y))
        return ImageTk.PhotoImage(canvas)

    def _set_preview_image(self, path: Path):
        img = safe_open_image(path)
        if img is None:
            self.preview_label.configure(text="Nem olvasható kép", image="")
            self._preview_ref = None
            return

        # Preview méretre
        base = img.copy()
        base.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", PREVIEW_SIZE, (240, 240, 240))
        x = (PREVIEW_SIZE[0] - base.size[0]) // 2
        y = (PREVIEW_SIZE[1] - base.size[1]) // 2
        if base.mode in ("RGBA", "LA"):
            canvas.paste(base, (x, y), base)
        else:
            canvas.paste(base, (x, y))

        self._preview_ref = ImageTk.PhotoImage(canvas)
        self.preview_label.configure(image=self._preview_ref, text="")


def main():
    folder = Path(IMAGES_DIR)
    app = SceneManagerGUI(folder)
    app.mainloop()


if __name__ == "__main__":
    main()