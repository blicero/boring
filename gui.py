#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2025-09-08 17:43:38 krylon>
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
        self.ticks_per_second: int = 0

        # Create the widgets.

        self.win = gtk.Window()
        self.win.set_title(f"{common.AppName} {common.AppVersion}")
        self.mbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)

        self.tick_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.cnt_lbl = gtk.Label.new("")
        self.tick_btn = gtk.Button.new_with_mnemonic("_Tick")
        self.tick_box.pack_start(self.tick_btn, False, True, 0)
        self.tick_box.pack_start(self.cnt_lbl, False, True, 0)

        self.upgrade_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.upgrade_btn = gtk.Button.new_with_mnemonic("_Upgrade")
        self.upgrade_price_entry = gtk.Entry()
        self.upgrade_lvl_lbl = gtk.Label.new("")
        self.upgrade_price_entry.set_editable(False)
        self.upgrade_box.pack_start(self.upgrade_btn, False, True, 0)
        self.upgrade_box.pack_start(self.upgrade_price_entry, False, True, 0)
        self.upgrade_box.pack_start(self.upgrade_lvl_lbl, False, True, 0)

        self.auto_box = gtk.Box(orientation=gtk.Orientation.HORIZONTAL)
        self.auto_buy_btn = gtk.Button.new_with_mnemonic("_Buy auto tick")
        self.auto_price_lbl = gtk.Label.new("")
        self.auto_lvl_lbl = gtk.Label.new("")
        self.auto_box.pack_start(self.auto_lvl_lbl, False, True, 4)
        self.auto_box.pack_start(self.auto_price_lbl, False, True, 4)
        self.auto_box.pack_start(self.auto_buy_btn, False, True, 4)

        self.mbox.pack_start(self.tick_box, False, True, 4)
        self.mbox.pack_start(self.upgrade_box, False, True, 4)
        self.mbox.pack_start(self.auto_box, False, True, 4)

        self.win.add(self.mbox)

        # Register signal handlers
        self.win.connect("destroy", self._quit)
        self.tick_btn.connect("clicked", self.tick)
        self.upgrade_btn.connect("clicked", self.buy_upgrade)
        self.auto_buy_btn.connect("clicked", self.buy_auto)
        glib.timeout_add(1000, self.periodic)

        self.win.show_all()
        self.win.visible = True

        self.render()

    def auto_price(self) -> int:
        """Calculate the price to buy an additional auto tick per second."""
        price = 1 << (self.ticks_per_second + 1)
        return price

    def periodic(self) -> bool:
        """Perform periodic tasks."""
        try:
            now: float = time.time()

            if now - self.last_tick > 1.0:
                for _ in range(self.ticks_per_second):
                    self.eng.tick()
                self.render()

            self.last_tick = now
        finally:
            return True  # noqa: B012  # pylint: disable-msg=W0134,W0150

    def run(self):
        """Execute the Gtk event loop."""
        gtk.main()

    def _quit(self, *_ignore):
        self.win.destroy()
        gtk.main_quit()

    def render(self) -> None:
        """Display the Engine's counter in the UI."""
        lbl: Final[str] = f"""<span size="x-large">{self.eng.cnt}</span>"""
        auto_price: Final[int] = self.auto_price()

        self.cnt_lbl.set_markup(lbl)
        self.upgrade_price_entry.set_text(f"{self.eng.upgrade_price}")
        self.upgrade_btn.set_sensitive(self.eng.can_upgrade)
        self.upgrade_lvl_lbl.set_text(f"{self.eng.lvl}")
        self.auto_lvl_lbl.set_text(f"{self.ticks_per_second}/sec.")
        self.auto_price_lbl.set_text(f"{self.auto_price()}")
        self.auto_buy_btn.set_sensitive(self.eng.cnt >= auto_price)

    def buy_upgrade(self, *_args) -> None:
        """Buy an upgrade."""
        self.eng.upgrade()
        self.render()

    def buy_auto(self, _arg) -> None:
        """Buy an additional auto tick per second."""
        price: Final[int] = self.auto_price()
        self.eng.cnt -= price
        self.ticks_per_second += 1
        self.render()

    def tick(self, *_args) -> None:
        """Advance the game by one tick."""
        self.eng.tick()
        self.render()


if __name__ == '__main__':
    g = GUI()
    g.run()

# Local Variables: #
# python-indent: 4 #
# End: #
