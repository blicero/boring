#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2025-09-08 11:13:16 krylon>
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
from typing import Final


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

    @property
    def upgrade_price(self) -> int:
        """Return the price to upgrade to the next level."""
        return (1 << (10 * self.lvl))

    @property
    def can_upgrade(self) -> bool:
        """Return True if we have sufficient points to upgrade."""
        return self.cnt >= self.upgrade_price

    def upgrade(self) -> None:
        """Perform an upgrade to the next level, if we have sufficient points."""
        price: Final[int] = self.upgrade_price
        if price <= self.cnt:
            self.cnt -= price
            self.lvl += 1

# Local Variables: #
# python-indent: 4 #
# End: #
