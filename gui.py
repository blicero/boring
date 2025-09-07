#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2025-09-07 22:51:49 krylon>
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

from threading import Lock

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
# from gi.repository import \
#     GLib as \
#     glib  # noqa: E402,F401 # pylint: disable-msg=C0413,C0411,W0611 # type: ignore
from gi.repository import \
    Gtk as \
    gtk  # noqa: E402,F401 # pylint: disable-msg=C0413,C0411,W0611 # type: ignore


class GUI:  # pylint: disable-msg=I1101,E1101,R0902
    """GUI is the graphical frontend to the boring idle-clicker game."""

    def __init__(self) -> None:
        self.log = common.get_logger("gui")
        self.lock = Lock()
        self.eng = Engine()

        # Create the widgets.

        self.win = gtk.Window()
        self.win.set_title(f"{common.AppName} {common.AppVersion}")
        self.mbox = gtk.Box(orientation=gtk.Orientation.VERTICAL)

        self.cnt_lbl = gtk.Label.new("")
        self.tick_btn = gtk.Button.new_with_mnemonic("_Tick")

        self.mbox.pack_start(self.cnt_lbl,
                             False,
                             True,
                             0)
        self.mbox.pack_start(self.tick_btn,
                             False,
                             True,
                             0)

        self.win.add(self.mbox)

        # Register signal handlers
        self.win.connect("destroy", self._quit)
        self.tick_btn.connect("clicked", self.tick)

        self.win.show_all()
        self.win.visible = True

    def run(self):
        """Execute the Gtk event loop."""
        gtk.main()

    def _quit(self, *_ignore):
        self.win.destroy()
        gtk.main_quit()

    def render(self) -> None:
        """Display the Engine's counter in the UI."""
        lbl: str = f"""<span size="x-large">{self.eng.cnt}</span>"""

        self.cnt_lbl.set_markup(lbl)

    def tick(self, *args) -> None:
        """Advance the game by one tick."""
        self.eng.tick()
        self.render()


if __name__ == '__main__':
    g = GUI()
    g.run()

# Local Variables: #
# python-indent: 4 #
# End: #
