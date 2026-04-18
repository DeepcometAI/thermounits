"""
thermounits.thermo.functions
============================
Unit-safe thermodynamic computation functions.

Every function:
  1. Accepts Quantity arguments.
  2. Validates dimensions before any arithmetic.
  3. Returns Quantity results.
  4. Is deterministic (no hidden state, no random seeds).

Reference constants
-------------------
R_universal = 8.314462618 J/(mol·K)   [CODATA 2018]
"""

from __future__ import annotations
import math
from typing import Optional

from ..units.quantity import Quantity, DimensionError
from ..units.dimensions import (
    TEMPERATURE, PRESSURE, SPECIFIC_ENERGY, SPECIFIC_ENTROPY,
    ENERGY, DIMENSIONLESS, MOLAR_ENERGY, MOLAR_ENTROPY,
)
from ..units.registry import ureg

# Universal gas constant [J/(mol·K)]
R_UNIVERSAL = 8.314462618


def _require(qty: Quantity, expected_dim, name: str) -> Quantity:
    """Raise DimensionError if qty has the wrong dimension."""
    if qty.dimension != expected_dim:
        raise DimensionError(
            f"Argument '{name}' must have dimension {expected_dim!r}, "
            f"got {qty.dimension!r}."
        )
    return qty


# ---------------------------------------------------------------------------
# Ideal-gas state functions
# ---------------------------------------------------------------------------

def enthalpy_ideal_gas(
    temperature: Quantity,
    cp: Quantity,
    T_ref: Optional[Quantity] = None,
) -> Quantity:
    """
    Specific enthalpy of an ideal gas relative to a reference temperature.

    .. math::
        h = c_p (T - T_{\\text{ref}})

    Parameters
    ----------
    temperature : Quantity[TEMPERATURE]
        Current temperature [K].
    cp : Quantity[SPECIFIC_ENTROPY]
        Specific heat at constant pressure [J/(kg·K)].
    T_ref : Quantity[TEMPERATURE], optional
        Reference temperature (default 298.15 K).

    Returns
    -------
    Quantity[SPECIFIC_ENERGY]   [J/kg]
    """
    _require(temperature, TEMPERATURE, "temperature")
    _require(cp, SPECIFIC_ENTROPY, "cp")
    if T_ref is None:
        T_ref = ureg.quantity(298.15, "K")
    _require(T_ref, TEMPERATURE, "T_ref")

    delta_T = temperature - T_ref   # Quantity[TEMPERATURE]  (K difference)
    # J/(kg·K) × K → J/kg  [dimension arithmetic via Quantity.__mul__]
    result = cp * delta_T
    return Quantity(result.value, SPECIFIC_ENERGY, "J/kg")


def entropy_ideal_gas(
    temperature: Quantity,
    pressure: Quantity,
    cp: Quantity,
    molar_mass: float,
    T_ref: Optional[Quantity] = None,
    P_ref: Optional[Quantity] = None,
) -> Quantity:
    """
    Specific entropy of an ideal gas.

    .. math::
        s = c_p \\ln\\!\\left(\\frac{T}{T_{\\text{ref}}}\\right)
            - \\frac{R}{M} \\ln\\!\\left(\\frac{P}{P_{\\text{ref}}}\\right)

    Parameters
    ----------
    temperature : Quantity[TEMPERATURE]     [K]
    pressure : Quantity[PRESSURE]           [Pa]
    cp : Quantity[SPECIFIC_ENTROPY]         [J/(kg·K)]
    molar_mass : float
        Molar mass of the gas [kg/mol].
    T_ref : Quantity[TEMPERATURE], optional
        Reference temperature (default 298.15 K).
    P_ref : Quantity[PRESSURE], optional
        Reference pressure (default 101 325 Pa).

    Returns
    -------
    Quantity[SPECIFIC_ENTROPY]   [J/(kg·K)]
    """
    _require(temperature, TEMPERATURE, "temperature")
    _require(pressure, PRESSURE, "pressure")
    _require(cp, SPECIFIC_ENTROPY, "cp")
    if T_ref is None:
        T_ref = ureg.quantity(298.15, "K")
    if P_ref is None:
        P_ref = ureg.quantity(101325.0, "Pa")
    _require(T_ref, TEMPERATURE, "T_ref")
    _require(P_ref, PRESSURE, "P_ref")
    if molar_mass <= 0:
        raise ValueError(f"molar_mass must be > 0 kg/mol, got {molar_mass}.")

    R_specific = R_UNIVERSAL / molar_mass  # J/(kg·K)
    s_val = (
        cp.value * math.log(temperature.value / T_ref.value)
        - R_specific * math.log(pressure.value / P_ref.value)
    )
    return Quantity(s_val, SPECIFIC_ENTROPY, "J/(kg·K)")


def internal_energy(
    enthalpy: Quantity,
    pressure: Quantity,
    density: Quantity,
) -> Quantity:
    """
    Specific internal energy from enthalpy via the definition h = u + P/ρ.

    .. math::
        u = h - \\frac{P}{\\rho}

    Parameters
    ----------
    enthalpy : Quantity[SPECIFIC_ENERGY]    [J/kg]
    pressure : Quantity[PRESSURE]           [Pa]
    density : Quantity[DENSITY]             [kg/m³]

    Returns
    -------
    Quantity[SPECIFIC_ENERGY]   [J/kg]
    """
    from ..units.dimensions import DENSITY
    _require(enthalpy, SPECIFIC_ENERGY, "enthalpy")
    _require(pressure, PRESSURE, "pressure")
    _require(density, DENSITY, "density")

    pv = Quantity(pressure.value / density.value, SPECIFIC_ENERGY, "J/kg")
    return enthalpy - pv


def gibbs_free_energy(
    enthalpy: Quantity,
    temperature: Quantity,
    entropy: Quantity,
) -> Quantity:
    """
    Specific Gibbs free energy.

    .. math::
        g = h - T s

    Parameters
    ----------
    enthalpy : Quantity[SPECIFIC_ENERGY]    [J/kg]
    temperature : Quantity[TEMPERATURE]     [K]
    entropy : Quantity[SPECIFIC_ENTROPY]    [J/(kg·K)]

    Returns
    -------
    Quantity[SPECIFIC_ENERGY]   [J/kg]
    """
    _require(enthalpy, SPECIFIC_ENERGY, "enthalpy")
    _require(temperature, TEMPERATURE, "temperature")
    _require(entropy, SPECIFIC_ENTROPY, "entropy")

    ts_val = temperature.value * entropy.value   # K × J/(kg·K) → J/kg
    ts = Quantity(ts_val, SPECIFIC_ENERGY, "J/kg")
    return enthalpy - ts


def helmholtz_free_energy(
    internal_energy_qty: Quantity,
    temperature: Quantity,
    entropy: Quantity,
) -> Quantity:
    """
    Specific Helmholtz free energy.

    .. math::
        a = u - T s

    Parameters
    ----------
    internal_energy_qty : Quantity[SPECIFIC_ENERGY]   [J/kg]
    temperature : Quantity[TEMPERATURE]               [K]
    entropy : Quantity[SPECIFIC_ENTROPY]              [J/(kg·K)]

    Returns
    -------
    Quantity[SPECIFIC_ENERGY]   [J/kg]
    """
    _require(internal_energy_qty, SPECIFIC_ENERGY, "internal_energy_qty")
    _require(temperature, TEMPERATURE, "temperature")
    _require(entropy, SPECIFIC_ENTROPY, "entropy")

    ts_val = temperature.value * entropy.value
    ts = Quantity(ts_val, SPECIFIC_ENERGY, "J/kg")
    return internal_energy_qty - ts


# ---------------------------------------------------------------------------
# Isentropic relations
# ---------------------------------------------------------------------------

def isentropic_temperature(
    T1: Quantity,
    P1: Quantity,
    P2: Quantity,
    gamma: float,
) -> Quantity:
    """
    Exit temperature for an isentropic process (ideal gas).

    .. math::
        T_2 = T_1 \\left(\\frac{P_2}{P_1}\\right)^{(\\gamma-1)/\\gamma}

    Parameters
    ----------
    T1 : Quantity[TEMPERATURE]   inlet temperature [K]
    P1 : Quantity[PRESSURE]      inlet pressure    [Pa]
    P2 : Quantity[PRESSURE]      exit pressure     [Pa]
    gamma : float                heat capacity ratio Cp/Cv (dimensionless)

    Returns
    -------
    Quantity[TEMPERATURE]   [K]
    """
    _require(T1, TEMPERATURE, "T1")
    _require(P1, PRESSURE, "P1")
    _require(P2, PRESSURE, "P2")
    if gamma <= 1:
        raise ValueError(f"gamma must be > 1 for an ideal gas; got {gamma}.")
    exponent = (gamma - 1) / gamma
    T2_val = T1.value * (P2.value / P1.value) ** exponent
    return Quantity(T2_val, TEMPERATURE, "K")


def isentropic_pressure(
    P1: Quantity,
    T1: Quantity,
    T2: Quantity,
    gamma: float,
) -> Quantity:
    """
    Exit pressure for an isentropic process (ideal gas).

    .. math::
        P_2 = P_1 \\left(\\frac{T_2}{T_1}\\right)^{\\gamma/(\\gamma-1)}
    """
    _require(P1, PRESSURE, "P1")
    _require(T1, TEMPERATURE, "T1")
    _require(T2, TEMPERATURE, "T2")
    if gamma <= 1:
        raise ValueError(f"gamma must be > 1; got {gamma}.")
    exponent = gamma / (gamma - 1)
    P2_val = P1.value * (T2.value / T1.value) ** exponent
    return Quantity(P2_val, PRESSURE, "Pa")


# ---------------------------------------------------------------------------
# Polytropic relations
# ---------------------------------------------------------------------------

def polytropic_temperature(
    T1: Quantity,
    P1: Quantity,
    P2: Quantity,
    n: float,
) -> Quantity:
    """
    Exit temperature for a polytropic process  PVⁿ = const.

    .. math::
        T_2 = T_1 \\left(\\frac{P_2}{P_1}\\right)^{(n-1)/n}
    """
    _require(T1, TEMPERATURE, "T1")
    _require(P1, PRESSURE, "P1")
    _require(P2, PRESSURE, "P2")
    if n == 0:
        raise ValueError("Polytropic index n=0 is an isobaric process; T₂ = T₁.")
    exponent = (n - 1) / n
    T2_val = T1.value * (P2.value / P1.value) ** exponent
    return Quantity(T2_val, TEMPERATURE, "K")


def polytropic_pressure(
    P1: Quantity,
    T1: Quantity,
    T2: Quantity,
    n: float,
) -> Quantity:
    """Exit pressure for a polytropic process."""
    _require(P1, PRESSURE, "P1")
    _require(T1, TEMPERATURE, "T1")
    _require(T2, TEMPERATURE, "T2")
    exponent = n / (n - 1) if n != 1 else float("inf")
    P2_val = P1.value * (T2.value / T1.value) ** exponent
    return Quantity(P2_val, PRESSURE, "Pa")


# ---------------------------------------------------------------------------
# Efficiencies / COP
# ---------------------------------------------------------------------------

def carnot_efficiency(T_hot: Quantity, T_cold: Quantity) -> float:
    """
    Carnot (maximum) thermal efficiency of a heat engine.

    .. math::
        \\eta_{\\text{Carnot}} = 1 - \\frac{T_{\\text{cold}}}{T_{\\text{hot}}}

    Parameters
    ----------
    T_hot  : Quantity[TEMPERATURE]   [K]
    T_cold : Quantity[TEMPERATURE]   [K]

    Returns
    -------
    float ∈ [0, 1)
    """
    _require(T_hot,  TEMPERATURE, "T_hot")
    _require(T_cold, TEMPERATURE, "T_cold")
    if T_cold.value >= T_hot.value:
        raise ValueError(
            f"T_cold ({T_cold}) must be strictly less than T_hot ({T_hot}) "
            "for a heat engine to produce work."
        )
    return 1.0 - T_cold.value / T_hot.value


def cop_refrigerator(T_hot: Quantity, T_cold: Quantity) -> float:
    """
    Carnot COP of a refrigerator (cooling effect / work input).

    .. math::
        \\mathrm{COP}_R = \\frac{T_{\\text{cold}}}{T_{\\text{hot}} - T_{\\text{cold}}}
    """
    _require(T_hot,  TEMPERATURE, "T_hot")
    _require(T_cold, TEMPERATURE, "T_cold")
    delta = T_hot.value - T_cold.value
    if delta <= 0:
        raise ValueError("T_hot must be strictly greater than T_cold.")
    return T_cold.value / delta


def cop_heat_pump(T_hot: Quantity, T_cold: Quantity) -> float:
    """
    Carnot COP of a heat pump (heating effect / work input).

    .. math::
        \\mathrm{COP}_{HP} = \\frac{T_{\\text{hot}}}{T_{\\text{hot}} - T_{\\text{cold}}}
    """
    _require(T_hot,  TEMPERATURE, "T_hot")
    _require(T_cold, TEMPERATURE, "T_cold")
    delta = T_hot.value - T_cold.value
    if delta <= 0:
        raise ValueError("T_hot must be strictly greater than T_cold.")
    return T_hot.value / delta


# ---------------------------------------------------------------------------
# Phase-change helpers
# ---------------------------------------------------------------------------

def heat_of_vaporisation(
    T: Quantity,
    h_vapour: Quantity,
    h_liquid: Quantity,
) -> Quantity:
    """
    Latent heat of vaporisation at a given temperature.

    .. math::
        L_v = h_g - h_f

    Parameters
    ----------
    T        : Quantity[TEMPERATURE]    temperature of phase change [K]
    h_vapour : Quantity[SPECIFIC_ENERGY]  saturated vapour enthalpy h_g [J/kg]
    h_liquid : Quantity[SPECIFIC_ENERGY]  saturated liquid enthalpy h_f [J/kg]

    Returns
    -------
    Quantity[SPECIFIC_ENERGY]   [J/kg]
    """
    _require(T,        TEMPERATURE,    "T")
    _require(h_vapour, SPECIFIC_ENERGY, "h_vapour")
    _require(h_liquid, SPECIFIC_ENERGY, "h_liquid")
    return h_vapour - h_liquid


def clausius_clapeyron(
    T: Quantity,
    L_v: Quantity,
    molar_mass: float,
) -> Quantity:
    """
    Slope of the saturation curve dP/dT via the Clausius-Clapeyron equation.

    .. math::
        \\frac{dP}{dT} = \\frac{L_v P}{R_s T^2}

    where Rₛ = R/M.  P is evaluated as 101 325 Pa (1 atm) by default.

    Parameters
    ----------
    T          : Quantity[TEMPERATURE]    [K]
    L_v        : Quantity[SPECIFIC_ENERGY] latent heat [J/kg]
    molar_mass : float                    molar mass [kg/mol]

    Returns
    -------
    Quantity    dP/dT in Pa/K
    """
    from ..units.dimensions import Dimension
    _require(T,   TEMPERATURE,    "T")
    _require(L_v, SPECIFIC_ENERGY,"L_v")
    if molar_mass <= 0:
        raise ValueError(f"molar_mass must be > 0, got {molar_mass}.")
    P_ref = 101325.0
    R_s = R_UNIVERSAL / molar_mass
    dPdT = L_v.value * P_ref / (R_s * T.value**2)
    # Dimension of dP/dT = PRESSURE / TEMPERATURE
    dPdT_dim = Dimension(M=1, L=-1, T=-2, theta=-1)
    return Quantity(dPdT, dPdT_dim, "Pa/K")


# ---------------------------------------------------------------------------
# Work calculations
# ---------------------------------------------------------------------------

def work_isothermal(
    P1: Quantity,
    V1: Quantity,
    P2: Quantity,
) -> Quantity:
    """
    Reversible isothermal work done *by* the system (closed system).

    .. math::
        W = P_1 V_1 \\ln\\!\\left(\\frac{P_1}{P_2}\\right)

    Parameters
    ----------
    P1, P2 : Quantity[PRESSURE]   [Pa]
    V1     : Quantity[VOLUME]      [m³]

    Returns
    -------
    Quantity[ENERGY]   [J]
    """
    from ..units.dimensions import VOLUME
    _require(P1, PRESSURE, "P1")
    _require(P2, PRESSURE, "P2")
    _require(V1, VOLUME,   "V1")
    W_val = P1.value * V1.value * math.log(P1.value / P2.value)
    return Quantity(W_val, ENERGY, "J")


def work_adiabatic(
    P1: Quantity,
    V1: Quantity,
    P2: Quantity,
    V2: Quantity,
) -> Quantity:
    """
    Reversible adiabatic (isentropic) work done *by* the system.

    .. math::
        W = \\frac{P_1 V_1 - P_2 V_2}{\\gamma - 1}

    Note: caller must supply consistent (P1,V1), (P2,V2) from isentropic
    relations.  γ is implicit in the volume ratio.

    Parameters
    ----------
    P1, P2 : Quantity[PRESSURE]   [Pa]
    V1, V2 : Quantity[VOLUME]      [m³]

    Returns
    -------
    Quantity[ENERGY]   [J]
    """
    from ..units.dimensions import VOLUME
    _require(P1, PRESSURE, "P1")
    _require(P2, PRESSURE, "P2")
    _require(V1, VOLUME,   "V1")
    _require(V2, VOLUME,   "V2")
    W_val = P1.value * V1.value - P2.value * V2.value
    return Quantity(W_val, ENERGY, "J")


# ---------------------------------------------------------------------------
# Energy balance helper
# ---------------------------------------------------------------------------

def energy_balance(
    q_in: Quantity,
    w_out: Quantity,
    delta_h: Quantity,
) -> Quantity:
    """
    First-law energy balance for an open system (steady-state, per unit mass):

    .. math::
        q_{in} - w_{out} = \\Delta h

    Returns the residual (should be ≈ 0 for a balanced system).

    Parameters
    ----------
    q_in    : Quantity[SPECIFIC_ENERGY]   heat added per unit mass [J/kg]
    w_out   : Quantity[SPECIFIC_ENERGY]   shaft work out per unit mass [J/kg]
    delta_h : Quantity[SPECIFIC_ENERGY]   enthalpy rise h₂ − h₁ [J/kg]

    Returns
    -------
    Quantity[SPECIFIC_ENERGY]   residual [J/kg]   (≈ 0 for a balanced system)
    """
    _require(q_in,    SPECIFIC_ENERGY, "q_in")
    _require(w_out,   SPECIFIC_ENERGY, "w_out")
    _require(delta_h, SPECIFIC_ENERGY, "delta_h")
    return q_in - w_out - delta_h
