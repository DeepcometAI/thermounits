"""
thermounits.fluids.air
======================
Thermodynamic properties of dry air modelled as an ideal gas.

Cp correlation valid 200 – 2000 K (Shomate equation, NIST WebBook):
  Cp°(T) = A + B·t + C·t² + D·t³ + E/t²     [J/(mol·K)]
  where t = T[K] / 1000
"""

from __future__ import annotations
import math

from ..units.quantity import Quantity
from ..units.dimensions import (
    TEMPERATURE, PRESSURE, SPECIFIC_ENERGY, SPECIFIC_ENTROPY, DENSITY,
)
from ..units.registry import ureg

# Air molar mass and gas constant
M_AIR = 0.0289647    # kg/mol
R_AIR = 8.314462618 / M_AIR   # 287.058 J/(kg·K)

# NIST Shomate coefficients for air (200–6000 K, two-piece fit)
# Source: NIST Chemistry WebBook — "Air" composite entry
# Cp°(T) = A + B·t + C·t² + D·t³ + E/t²  where t = T[K]/1000
# Units: Cp in J/(mol·K)
#
# Low range  200 – 1000 K:
_SHOMATE_LOW  = (28.11, 1.967983, 4.802052, -1.966279, 0.079600)
# High range 1000 – 6000 K:
_SHOMATE_HIGH = (19.50583, 19.88705, -8.498699, 1.372751, 0.527601)


def cp_air_molar(T_K: float) -> float:
    """Molar heat capacity of air [J/(mol·K)] at temperature T_K."""
    t = T_K / 1000.0
    A, B, C, D, E = _SHOMATE_LOW if T_K <= 1000 else _SHOMATE_HIGH
    return A + B*t + C*t**2 + D*t**3 + E/t**2


def cp_air(T_K: float) -> float:
    """Specific heat of air at constant pressure [J/(kg·K)] at T_K."""
    return cp_air_molar(T_K) / M_AIR


def cv_air(T_K: float) -> float:
    """Specific heat of air at constant volume [J/(kg·K)] at T_K."""
    return cp_air(T_K) - R_AIR


def gamma_air(T_K: float) -> float:
    """Heat-capacity ratio of air Cp/Cv at T_K."""
    cp = cp_air(T_K)
    return cp / (cp - R_AIR)


def _integrate_cp(T1_K: float, T2_K: float, steps: int = 200) -> float:
    """Numerical integration of cp(T) dT from T1 to T2 [J/kg]."""
    if T1_K == T2_K:
        return 0.0
    dT = (T2_K - T1_K) / steps
    result = 0.0
    T = T1_K + 0.5 * dT
    for _ in range(steps):
        result += cp_air(T) * dT
        T += dT
    return result


def _integrate_cp_over_T(T1_K: float, T2_K: float, steps: int = 200) -> float:
    """Numerical integration of cp(T)/T dT from T1 to T2 [J/(kg·K)]."""
    if T1_K == T2_K:
        return 0.0
    dT = (T2_K - T1_K) / steps
    result = 0.0
    T = T1_K + 0.5 * dT
    for _ in range(steps):
        result += cp_air(T) / T * dT
        T += dT
    return result


class AirProperties:
    """
    Ideal-gas thermodynamic properties of dry air.

    Examples
    --------
    >>> ap = AirProperties()
    >>> state = ap.at_T_P(ureg.quantity(25, "°C"), ureg.quantity(101325, "Pa"))
    >>> print(state.enthalpy.to("kJ/kg"))
    """

    T_REF = 298.15    # K  (standard reference temperature)
    P_REF = 101325.0  # Pa (standard reference pressure)

    def at_T_P(self, temperature: Quantity, pressure: Quantity):
        """
        Compute a ThermodynamicState for air at (T, P).

        Parameters
        ----------
        temperature : Quantity[TEMPERATURE]
        pressure    : Quantity[PRESSURE]

        Returns
        -------
        ThermodynamicState
        """
        from ..thermo.state import ThermodynamicState
        from ..thermo.phase import PhaseState

        T_K = temperature.value
        P_Pa = pressure.value

        h_val = _integrate_cp(self.T_REF, T_K)
        s_val = (
            _integrate_cp_over_T(self.T_REF, T_K)
            - R_AIR * math.log(P_Pa / self.P_REF)
        )
        rho_val = P_Pa / (R_AIR * T_K)
        cp_val = cp_air(T_K)

        return ThermodynamicState(
            temperature=temperature,
            pressure=pressure,
            enthalpy=Quantity(h_val, SPECIFIC_ENERGY, "J/kg"),
            entropy=Quantity(s_val, SPECIFIC_ENTROPY, "J/(kg·K)"),
            density=Quantity(rho_val, DENSITY, "kg/m³"),
            phase=PhaseState.GAS,
            fluid="air",
        )

    def cp(self, temperature: Quantity) -> Quantity:
        """Specific heat Cp of air [J/(kg·K)]."""
        return Quantity(cp_air(temperature.value), SPECIFIC_ENTROPY, "J/(kg·K)")

    def cv(self, temperature: Quantity) -> Quantity:
        """Specific heat Cv of air [J/(kg·K)]."""
        return Quantity(cv_air(temperature.value), SPECIFIC_ENTROPY, "J/(kg·K)")

    def gamma(self, temperature: Quantity) -> float:
        """Heat-capacity ratio γ = Cp/Cv of air (dimensionless)."""
        return gamma_air(temperature.value)

    def density(self, temperature: Quantity, pressure: Quantity) -> Quantity:
        """Density of air [kg/m³] from ideal gas law."""
        rho = pressure.value / (R_AIR * temperature.value)
        return Quantity(rho, DENSITY, "kg/m³")

    def speed_of_sound(self, temperature: Quantity) -> Quantity:
        """Speed of sound in air [m/s]."""
        from ..units.dimensions import VELOCITY
        T_K = temperature.value
        g = gamma_air(T_K)
        c = math.sqrt(g * R_AIR * T_K)
        return Quantity(c, VELOCITY, "m/s")
