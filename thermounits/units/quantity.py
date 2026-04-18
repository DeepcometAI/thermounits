"""
thermounits.units.quantity
==========================
The central Quantity type.  Every measurement in thermounits is a
Quantity so that dimensional errors are caught at computation time
rather than silently producing wrong answers.

Design goals
------------
* Immutable after construction.
* Full arithmetic with automatic dimension checking.
* Lossless SI-internal representation — conversions happen only at
  I/O boundaries (construction / display / export).
* Informative error messages that name the conflicting dimensions.
"""

from __future__ import annotations
import math
from typing import Union

from .dimensions import Dimension, DIMENSIONLESS

Number = Union[int, float]


class DimensionError(TypeError):
    """Raised when an operation is attempted on incompatible dimensions."""


class Quantity:
    """
    A physical quantity: a numeric value paired with a Dimension.

    Parameters
    ----------
    value : float
        Magnitude in SI base units.
    dimension : Dimension
        Physical dimension of the quantity.
    unit_label : str, optional
        Human-readable unit string for display (e.g. ``"J/kg"``).

    Examples
    --------
    >>> from thermounits.units import ureg
    >>> T = ureg.quantity(300, "K")
    >>> P = ureg.quantity(101325, "Pa")
    >>> T
    300.0 K
    """

    __slots__ = ("_value", "_dimension", "_unit_label")

    def __init__(
        self,
        value: Number,
        dimension: Dimension,
        unit_label: str = "",
    ) -> None:
        object.__setattr__(self, "_value", float(value))
        object.__setattr__(self, "_dimension", dimension)
        object.__setattr__(self, "_unit_label", unit_label)

    # ------------------------------------------------------------------
    # Properties (read-only)
    # ------------------------------------------------------------------

    @property
    def value(self) -> float:
        """Magnitude in SI base units."""
        return self._value

    @property
    def dimension(self) -> Dimension:
        """Physical dimension."""
        return self._dimension

    @property
    def unit_label(self) -> str:
        """Display unit label."""
        return self._unit_label

    # ------------------------------------------------------------------
    # Immutability guard
    # ------------------------------------------------------------------

    def __setattr__(self, name, value):
        raise AttributeError("Quantity objects are immutable.")

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        label = self._unit_label or str(self._dimension)
        return f"{self._value:g} {label}"

    def __str__(self) -> str:
        return self.__repr__()

    def __format__(self, spec: str) -> str:
        label = self._unit_label or str(self._dimension)
        return f"{self._value:{spec}} {label}"

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def _check_same_dim(self, other: "Quantity", op: str) -> None:
        if not isinstance(other, Quantity):
            raise DimensionError(
                f"Cannot compare Quantity with {type(other).__name__}."
            )
        if self._dimension != other._dimension:
            raise DimensionError(
                f"Dimension mismatch in '{op}': "
                f"{self._dimension!r} vs {other._dimension!r}"
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_same_dim(other, "==")
        return math.isclose(self._value, other._value, rel_tol=1e-9)

    def __lt__(self, other: "Quantity") -> bool:
        self._check_same_dim(other, "<")
        return self._value < other._value

    def __le__(self, other: "Quantity") -> bool:
        self._check_same_dim(other, "<=")
        return self._value <= other._value

    def __gt__(self, other: "Quantity") -> bool:
        self._check_same_dim(other, ">")
        return self._value > other._value

    def __ge__(self, other: "Quantity") -> bool:
        self._check_same_dim(other, ">=")
        return self._value >= other._value

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def __add__(self, other: "Quantity") -> "Quantity":
        self._check_same_dim(other, "+")
        return Quantity(
            self._value + other._value,
            self._dimension,
            self._unit_label,
        )

    def __sub__(self, other: "Quantity") -> "Quantity":
        self._check_same_dim(other, "-")
        return Quantity(
            self._value - other._value,
            self._dimension,
            self._unit_label,
        )

    def __mul__(self, other: Union["Quantity", Number]) -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(
                self._value * other._value,
                self._dimension * other._dimension,
            )
        return Quantity(self._value * other, self._dimension, self._unit_label)

    def __rmul__(self, other: Number) -> "Quantity":
        return self.__mul__(other)

    def __truediv__(self, other: Union["Quantity", Number]) -> "Quantity":
        if isinstance(other, Quantity):
            if other._value == 0:
                raise ZeroDivisionError("Division by zero-valued Quantity.")
            return Quantity(
                self._value / other._value,
                self._dimension / other._dimension,
            )
        if other == 0:
            raise ZeroDivisionError("Division by zero.")
        return Quantity(self._value / other, self._dimension, self._unit_label)

    def __rtruediv__(self, other: Number) -> "Quantity":
        if self._value == 0:
            raise ZeroDivisionError("Division by zero-valued Quantity.")
        return Quantity(
            other / self._value,
            DIMENSIONLESS / self._dimension,
        )

    def __pow__(self, exp: int) -> "Quantity":
        return Quantity(self._value**exp, self._dimension**exp)

    def __neg__(self) -> "Quantity":
        return Quantity(-self._value, self._dimension, self._unit_label)

    def __abs__(self) -> "Quantity":
        return Quantity(abs(self._value), self._dimension, self._unit_label)

    def __float__(self) -> float:
        return self._value

    def __hash__(self):
        return hash((round(self._value, 12), self._dimension))

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def to(self, target_unit: str) -> "Quantity":
        """
        Convert this quantity to *target_unit* and return a new Quantity
        whose ``unit_label`` reflects the requested unit.

        Conversion factors are looked up from the global registry.

        Examples
        --------
        >>> T = ureg.quantity(300, "K")
        >>> T.to("°C")
        26.85 °C
        """
        from .registry import ureg as _ureg
        return _ureg.convert(self, target_unit)

    def magnitude_in(self, target_unit: str) -> float:
        """Return only the numeric magnitude after converting to *target_unit*."""
        return self.to(target_unit).value

    def is_compatible_with(self, other: "Quantity") -> bool:
        """True if ``other`` has the same physical dimension."""
        return self._dimension == other._dimension
