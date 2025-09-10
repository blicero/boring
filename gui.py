#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2025-09-10 18:17:25 krylon>
#
# /data/code/python/boring/gui.py
# created on 07. 09. 2025
# (c) 2025 Benjamin Walkenhorst
#
# This file is part of the PyKuang network scanner. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
boring.gui

(c) 2025 Benjamin Walkenhorst
"""

import os
import pickle
import time
from threading import Lock
from typing import Final

import gi  # type: ignore

from boring import common
from boring.engine import Engine

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")

# from gi.repository import \
#     Gdk as \
#     gdk  # noqa: E402,F401 # pylint: disable-msg=C0413,C0411,W0611 # type: ignore
from gi.repository import \
    GLib as \
    glib  # noqa: E402,F401 # pylint: disable-msg=C0413,C0411,W0611 # type: ignore
from gi.repository import \
    Gtk as \
    gtk  # noqa: E402,F401 # pylint: disable-msg=C0413,C0411,W0611 # type: ignore


class GUI:  # pylint: disable-msg=I1101,E1101,R0902
    """GUI is the graphical frontend to the boring idle-clicker game."""

    def __init__(self) -> None:
        self.log = common.get_logger("gui")
        self.lock = Lock()
        self.eng = Engine()
        self.last_tick: float = 0.0
        self.active: bool = True

        # Create the widgets.

        self.win = gtk.Window()
        self.win.set_title(f"{common.AppName} {common.AppVersion}")
        self.grid = gtk.Grid()

        self.cnt_lbl = gtk.Label.new("")
        self.tick_btn = gtk.Button.new_with_mnemonic("_Tick")

        self.upgrade_btn = gtk.Button.new_with_mnemonic("_Upgrade")
        self.upgrade_price_entry = gtk.Entry()
        self.upgrade_lvl_lbl = gtk.Label.new("")
        self.upgrade_price_entry.set_editable(False)

        self.auto_buy_btn = gtk.Button.new_with_mnemonic("_Buy auto tick")
        self.auto_price_lbl = gtk.Label.new("")
        self.auto_lvl_lbl = gtk.Label.new("")

        self.pause_btn = gtk.Button.new_with_mnemonic("_Pause")
        self.reset_btn = gtk.Button.new_with_mnemonic("_Reset")
        self.save_btn = gtk.Button.new_with_mnemonic("_Save")
        self.load_btn = gtk.Button.new_with_mnemonic("_Load")

        # Assemble the widgets
        row: int = 0

        self.grid.attach(self.tick_btn, 0, row, 1, 1)
        self.grid.attach(self.cnt_lbl, 1, row, 3, 1)
        row += 1

        self.grid.attach(self.upgrade_btn, 0, row, 1, 1)
        self.grid.attach(self.upgrade_price_entry, 1, row, 3, 1)
        self.grid.attach(self.upgrade_lvl_lbl, 5, row, 2, 1)

        row += 1
        self.grid.attach(self.auto_buy_btn, 0, row, 1, 1)
        self.grid.attach(self.auto_price_lbl, 1, row, 3, 1)
        self.grid.attach(self.auto_lvl_lbl, 5, row, 1, 1)

        row += 1
        self.grid.attach(self.pause_btn, 0, row, 2, 1)
        self.grid.attach(self.reset_btn, 2, row, 2, 1)

        row += 1
        self.grid.attach(self.save_btn, 0, row, 2, 1)
        self.grid.attach(self.load_btn, 2, row, 2, 1)

        self.win.add(self.grid)

        # Register signal handlers
        self.win.connect("destroy", self._quit)
        self.tick_btn.connect("clicked", self.tick)
        self.upgrade_btn.connect("clicked", self.buy_upgrade)
        self.auto_buy_btn.connect("clicked", self.buy_auto)
        self.pause_btn.connect("clicked", self.toggle_pause)
        self.reset_btn.connect("clicked", self.reset_handler)
        self.save_btn.connect("clicked", self.save)
        self.load_btn.connect("clicked", self.load)
        glib.timeout_add(1000, self.periodic)

        self.win.show_all()
        self.win.visible = True

        if os.path.isfile(common.path.state()):
            self.load()

        self.render()

    def save(self, _btn=None) -> None:
        """Save the state of the game."""
        with open(common.path.state(), "wb") as fh:
            pickle.dump(self.eng, fh)

    def load(self, _btn=None) -> None:
        """Restore the state of the game from the save file."""
        with open(common.path.state(), "rb") as fh:
            self.eng = pickle.load(fh)

    def auto_price(self) -> int:
        """Calculate the price to buy an additional auto tick per second."""
        price = 1 << (self.eng.ticks_per_second + 1)
        return price

    def periodic(self) -> bool:
        """Perform periodic tasks."""
        if not self.active:
            return True
        try:
            now: float = time.time()

            if now - self.last_tick > 1.0:
                for _ in range(self.eng.ticks_per_second):
                    self.eng.tick()
                self.render()

            self.last_tick = now
        finally:
            return True  # noqa: B012  # pylint: disable-msg=W0134,W0150

    def run(self):
        """Execute the Gtk event loop."""
        gtk.main()

    def _quit(self, *_ignore):
        self.save()
        self.win.destroy()
        gtk.main_quit()

    def render(self) -> None:
        """Display the Engine's counter in the UI."""
        lbl: Final[str] = f"""<span size="24pt">{self.eng.cnt}</span>"""
        auto_price: Final[int] = self.auto_price()

        self.cnt_lbl.set_markup(lbl)
        self.upgrade_price_entry.set_text(f"{self.eng.upgrade_price}")
        self.upgrade_btn.set_sensitive(self.eng.can_upgrade)
        self.upgrade_lvl_lbl.set_markup(f"<tt>{self.eng.lvl}</tt>")
        self.auto_lvl_lbl.set_markup(f"<tt>{self.eng.ticks_per_second}/sec.</tt>")
        self.auto_price_lbl.set_markup(f"<tt>{self.auto_price()}</tt>")
        self.auto_buy_btn.set_sensitive(self.eng.cnt >= auto_price)

    def buy_upgrade(self, *_args) -> None:
        """Buy an upgrade."""
        self.eng.upgrade()
        self.render()

    def buy_auto(self, _arg) -> None:
        """Buy an additional auto tick per second."""
        price: Final[int] = self.auto_price()
        self.eng.cnt -= price
        self.eng.ticks_per_second += 1
        self.render()

    def tick(self, *_args) -> None:
        """Advance the game by one tick."""
        self.eng.tick()
        self.render()

    def toggle_pause(self, _widget) -> None:
        """Toggle the auto-tick."""
        self.active = not self.active

    def reset_handler(self, _widget) -> None:
        """Reset the game to its initial state."""
        self.eng.reset()

    def ask_yes_no(self, question: str, descr: str = "") -> bool:
        """Present a dialog asking a yes or no question, return True for yes, False for no"""
        dlg = gtk.Dialog(
            parent=self.win,
            title=question,
            modal=True,
        )

        dlg.add_buttons(
            gtk.STOCK_NO,
            gtk.ResponseType.NO,
            gtk.STOCK_YES,
            gtk.ResponseType.YES,
        )

        area = dlg.get_content_area()
        lblq = gtk.Label(label=question)
        area.add(lblq)
        if descr != "":
            lbld = gtk.Label(label=descr)
            area.add(lbld)

        dlg.show_all()

        try:
            response = dlg.run()
            match response:
                case gtk.ResponseType.YES:
                    return True
                case gtk.ResponseType.NO:
                    return False
                case other:
                    msg: Final[str] = f"CANTHAPPEN: Yes-or-No-Dialog returned {other}"
                    self.log.error(msg)
                    self.display_msg(msg)
                    return False
        finally:
            dlg.destroy()

    def display_msg(self, msg: str) -> None:
        """Display a message in a dialog."""
        self.log.info(msg)

        dlg = gtk.Dialog(
            parent=self.win,
            title="Attention",
            modal=True,
        )

        dlg.add_buttons(
            gtk.STOCK_OK,
            gtk.ResponseType.OK,
        )

        area = dlg.get_content_area()
        lbl = gtk.Label(label=msg)
        area.add(lbl)
        dlg.show_all()  # pylint: disable-msg=E1101

        try:
            dlg.run()  # pylint: disable-msg=E1101
        finally:
            dlg.destroy()


if __name__ == '__main__':
    g = GUI()
    g.run()

# Local Variables: #
# python-indent: 4 #
# End: #
