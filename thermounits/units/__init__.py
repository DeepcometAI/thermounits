"""
thermounits.units
=================
Unit-safe Quantity class and unit conversion registry.
Every thermodynamic value in thermounits is a Quantity — a float paired
with a physical dimension so that mismatched operations raise immediately.
"""

from .quantity import Quantity
from .registry import UnitRegistry, ureg
from .dimensions import Dimension

__all__ = ["Quantity", "UnitRegistry", "ureg", "Dimension"]
