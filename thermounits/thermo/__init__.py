"""
thermounits.thermo
==================
Core thermodynamic state functions.

All public functions accept and return :class:`~thermounits.units.Quantity`
objects so that dimensional safety is guaranteed end-to-end.

Included
--------
* Ideal-gas state functions (Cp, Cv, γ, h, s, g, a, u)
* Fundamental relations (first & second law residuals)
* Isentropic and polytropic relations
* COP / efficiency helpers
"""

from .state import ThermodynamicState
from .functions import (
    enthalpy_ideal_gas,
    entropy_ideal_gas,
    gibbs_free_energy,
    helmholtz_free_energy,
    internal_energy,
    isentropic_temperature,
    isentropic_pressure,
    polytropic_temperature,
    polytropic_pressure,
    carnot_efficiency,
    cop_heat_pump,
    cop_refrigerator,
    heat_of_vaporisation,
    clausius_clapeyron,
    work_isothermal,
    work_adiabatic,
    energy_balance,
)
from .phase import PhaseState, phase_of_water, phase_of_air

__all__ = [
    "ThermodynamicState",
    "enthalpy_ideal_gas",
    "entropy_ideal_gas",
    "gibbs_free_energy",
    "helmholtz_free_energy",
    "internal_energy",
    "isentropic_temperature",
    "isentropic_pressure",
    "polytropic_temperature",
    "polytropic_pressure",
    "carnot_efficiency",
    "cop_heat_pump",
    "cop_refrigerator",
    "heat_of_vaporisation",
    "clausius_clapeyron",
    "work_isothermal",
    "work_adiabatic",
    "energy_balance",
    "PhaseState",
    "phase_of_water",
    "phase_of_air",
]
