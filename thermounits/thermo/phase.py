"""
thermounits.thermo.phase
========================
Deterministic phase classification for supported fluids.

Phase boundaries use well-established correlations:
  * Water:  IAPWS-IF97 simplified saturation curve
  * Air:    ideal-gas throughout (no condensation model; treated as
            permanent gas above –140 °C)
"""

from __future__ import annotations
import math
from enum import Enum


class PhaseState(Enum):
    """Enumeration of thermodynamic phases."""
    SUBCOOLED_LIQUID   = "subcooled liquid"
    SATURATED_LIQUID   = "saturated liquid"
    TWO_PHASE          = "two-phase mixture"
    SATURATED_VAPOUR   = "saturated vapour"
    SUPERHEATED_VAPOUR = "superheated vapour"
    SUPERCRITICAL      = "supercritical fluid"
    GAS                = "gas"               # ideal / permanent gas


# ---------------------------------------------------------------------------
# Water — IAPWS-IF97 simplified saturation pressure correlation
# Reference: Wagner & Kruse, 2008  (Region 4)
# ---------------------------------------------------------------------------

_WATER_TRIPLE_T  = 273.16        # K
_WATER_TRIPLE_P  = 611.657       # Pa
_WATER_CRIT_T    = 647.096       # K
_WATER_CRIT_P    = 22.064e6      # Pa

# Antoine-style coefficients (IAPWS-IF97, Region 4 — Equation 30)
_N = [
     0.11670521452767e4,
    -0.72421316703206e6,
    -0.17073846940092e2,
     0.12020824702470e5,
    -0.32325550322333e7,
     0.14915108613530e2,
    -0.48232657361591e4,
     0.40511340542057e6,
    -0.23855557567849,
     0.65017534844798e3,
]


def sat_pressure_water(T_K: float) -> float:
    """
    Saturation pressure of water [Pa] at temperature *T_K* [K].

    Valid range: 273.15 K – 647.096 K (triple point to critical point).
    Uses the IAPWS-IF97 Region 4 backwards equation.
    """
    if T_K < _WATER_TRIPLE_T or T_K > _WATER_CRIT_T:
        raise ValueError(
            f"sat_pressure_water: T={T_K:.2f} K is outside valid range "
            f"[{_WATER_TRIPLE_T}, {_WATER_CRIT_T}] K."
        )
    theta = T_K + _N[8] / (T_K - _N[9])
    A = theta**2 + _N[0] * theta + _N[1]
    B = _N[2] * theta**2 + _N[3] * theta + _N[4]
    C = _N[5] * theta**2 + _N[6] * theta + _N[7]
    x = 2 * C / (-B + math.sqrt(B**2 - 4 * A * C))
    return (x**4) * 1e6   # convert MPa → Pa


def sat_temperature_water(P_Pa: float) -> float:
    """
    Saturation temperature of water [K] at pressure *P_Pa* [Pa].

    Valid range: 611.657 Pa – 22.064 MPa.
    Uses the IAPWS-IF97 Region 4 backwards equation.
    """
    if P_Pa < _WATER_TRIPLE_P or P_Pa > _WATER_CRIT_P:
        raise ValueError(
            f"sat_temperature_water: P={P_Pa:.1f} Pa is outside valid range "
            f"[{_WATER_TRIPLE_P:.1f}, {_WATER_CRIT_P:.6e}] Pa."
        )
    beta = (P_Pa * 1e-6) ** 0.25   # MPa^0.25
    E = beta**2 + _N[2] * beta + _N[5]
    F = _N[0] * beta**2 + _N[3] * beta + _N[6]
    G = _N[1] * beta**2 + _N[4] * beta + _N[7]
    D = 2 * G / (-F - math.sqrt(F**2 - 4 * E * G))
    return (_N[9] + D - math.sqrt((_N[9] + D)**2 - 4 * (_N[8] + _N[9] * D))) / 2


def phase_of_water(T_K: float, P_Pa: float) -> PhaseState:
    """
    Determine the thermodynamic phase of water given temperature and pressure.

    Parameters
    ----------
    T_K : float
        Temperature in Kelvin.
    P_Pa : float
        Pressure in Pascal.

    Returns
    -------
    PhaseState
    """
    # Supercritical region
    if T_K >= _WATER_CRIT_T and P_Pa >= _WATER_CRIT_P:
        return PhaseState.SUPERCRITICAL

    # Below triple point → ice (solid), out of scope — raise
    if T_K < _WATER_TRIPLE_T:
        raise ValueError(
            f"T={T_K:.2f} K is below the triple point of water "
            f"({_WATER_TRIPLE_T} K). Ice / solid phase not modelled."
        )

    if T_K > _WATER_CRIT_T:
        # Above critical temp, below crit pressure → superheated vapour
        return PhaseState.SUPERHEATED_VAPOUR

    p_sat = sat_pressure_water(T_K)
    tol = 1e-4 * p_sat  # 0.01 % tolerance for "on the curve"

    if P_Pa > p_sat + tol:
        return PhaseState.SUBCOOLED_LIQUID
    elif P_Pa < p_sat - tol:
        return PhaseState.SUPERHEATED_VAPOUR
    else:
        return PhaseState.TWO_PHASE   # on saturation curve


# ---------------------------------------------------------------------------
# Air — treated as a permanent ideal gas
# ---------------------------------------------------------------------------

_AIR_DEW_T = 133.0   # K  (approx. liquefaction onset at 1 atm)


def phase_of_air(T_K: float, _P_Pa: float = 101325.0) -> PhaseState:
    """
    Approximate phase of air.

    Air is modelled as an ideal gas above ~133 K.  Below this temperature
    a ValueError is raised because the ideal-gas model breaks down.

    Parameters
    ----------
    T_K : float
        Temperature in Kelvin.
    _P_Pa : float
        Pressure (not currently used; air treated as permanent gas).
    """
    if T_K < _AIR_DEW_T:
        raise ValueError(
            f"T={T_K:.2f} K is below the approximate liquefaction "
            f"temperature of air ({_AIR_DEW_T} K). "
            "Liquid-air properties are not modelled in this version."
        )
    return PhaseState.GAS
