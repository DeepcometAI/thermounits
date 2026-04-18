"""
thermounits.units.dimensions
============================
Represents physical dimensions as integer exponent vectors over the
seven SI base quantities:  M L T Θ I N J
(mass, length, time, temperature, current, amount, luminosity)

Only the thermodynamically relevant subset (M, L, T, Θ, N) is used
throughout the library, but the full vector is stored for completeness.
"""

from __future__ import annotations
from typing import NamedTuple


class Dimension(NamedTuple):
    """
    Seven-tuple of integer exponents for SI base dimensions.

    Attributes
    ----------
    M : int  — mass (kg)
    L : int  — length (m)
    T : int  — time (s)
    theta : int  — thermodynamic temperature (K)
    I : int  — electric current (A)
    N : int  — amount of substance (mol)
    J : int  — luminous intensity (cd)
    """

    M: int = 0      # mass
    L: int = 0      # length
    T: int = 0      # time
    theta: int = 0  # temperature
    I: int = 0      # electric current
    N: int = 0      # amount of substance
    J: int = 0      # luminous intensity

    # ------------------------------------------------------------------
    # Arithmetic on dimensions (for derived unit composition)
    # ------------------------------------------------------------------

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(*(a + b for a, b in zip(self, other)))

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(*(a - b for a, b in zip(self, other)))

    def __pow__(self, exp: int) -> "Dimension":
        return Dimension(*(a * exp for a in self))

    def __repr__(self) -> str:
        labels = ["M", "L", "T", "Θ", "I", "N", "J"]
        parts = [f"{l}^{e}" for l, e in zip(labels, self) if e != 0]
        return f"Dimension({' · '.join(parts) or 'dimensionless'})"

    def is_dimensionless(self) -> bool:
        return all(e == 0 for e in self)


# ---------------------------------------------------------------------------
# Pre-defined dimensions used throughout thermounits
# ---------------------------------------------------------------------------

DIMENSIONLESS   = Dimension()
MASS            = Dimension(M=1)
LENGTH          = Dimension(L=1)
TIME            = Dimension(T=1)
TEMPERATURE     = Dimension(theta=1)
AMOUNT          = Dimension(N=1)

AREA            = Dimension(L=2)
VOLUME          = Dimension(L=3)
VELOCITY        = Dimension(L=1, T=-1)
ACCELERATION    = Dimension(L=1, T=-2)

FORCE           = Dimension(M=1, L=1, T=-2)          # N = kg·m·s⁻²
PRESSURE        = Dimension(M=1, L=-1, T=-2)          # Pa = kg·m⁻¹·s⁻²
ENERGY          = Dimension(M=1, L=2, T=-2)           # J = kg·m²·s⁻²
POWER           = Dimension(M=1, L=2, T=-3)           # W = kg·m²·s⁻³

# Specific quantities (per unit mass)
SPECIFIC_ENERGY    = Dimension(L=2, T=-2)             # J/kg
SPECIFIC_ENTROPY   = Dimension(L=2, T=-2, theta=-1)   # J/(kg·K)

# Molar quantities
MOLAR_ENERGY       = Dimension(M=1, L=2, T=-2, N=-1)  # J/mol
MOLAR_ENTROPY      = Dimension(M=1, L=2, T=-2, theta=-1, N=-1)  # J/(mol·K)

HEAT_CAPACITY      = Dimension(M=1, L=2, T=-2, theta=-1)        # J/K
SPEC_HEAT_CAPACITY = Dimension(L=2, T=-2, theta=-1)              # J/(kg·K)

DENSITY         = Dimension(M=1, L=-3)                # kg/m³
DYNAMIC_VISCOSITY = Dimension(M=1, L=-1, T=-1)        # Pa·s
THERMAL_CONDUCTIVITY = Dimension(M=1, L=1, T=-3, theta=-1)  # W/(m·K)
