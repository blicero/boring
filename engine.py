#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2025-09-07 22:33:53 krylon>
#
# /data/code/python/boring/engine.py
# created on 07. 09. 2025
# (c) 2025 Benjamin Walkenhorst
#
# This file is part of the PyKuang network scanner. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
boring.engine

(c) 2025 Benjamin Walkenhorst
"""


from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class Engine:
    """Engine is the heart, if you will, of the game."""

    step: int = 0
    cnt: int = 0
    lvl: int = 0

    def tick(self) -> None:
        """Advance the game state by one tick."""
        self.step += 1
        self.cnt += (1 << self.lvl)

# Local Variables: #
# python-indent: 4 #
# End: #
