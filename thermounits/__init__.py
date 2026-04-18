"""
thermounits
===========
Unit-safe thermodynamics and heat transfer computations.

Quick start
-----------
Python API::

    from thermounits.units import ureg
    from thermounits.thermo import gibbs_free_energy
    from thermounits.fluids import WaterProperties

    T = ureg.quantity(400, "K")
    P = ureg.quantity(500_000, "Pa")
    wp = WaterProperties()
    state = wp.at_T_P(T, P)
    print(state)

CLI::

    $ thermounits convert 100 degC K
    $ thermounits steam --temp 200 --temp-unit degC --pressure 1 --pressure-unit MPa
    $ thermounits air --temp 25 --temp-unit degC
    $ thermounits isentropic --T1 300 --P1 100 --P2 500 --gamma 1.4
    $ thermounits carnot --T-hot 800 --T-cold 300
    $ thermounits gibbs --enthalpy 2500 --temp 400 --entropy 6.7
    $ thermounits phase water --temp 100 --temp-unit degC --pressure 101325
    $ thermounits fluids
"""

from .units import Quantity, ureg, UnitRegistry, Dimension
from .thermo import (
    ThermodynamicState,
    enthalpy_ideal_gas,
    entropy_ideal_gas,
    gibbs_free_energy,
    helmholtz_free_energy,
    internal_energy,
    isentropic_temperature,
    isentropic_pressure,
    carnot_efficiency,
    cop_heat_pump,
    cop_refrigerator,
    heat_of_vaporisation,
    energy_balance,
    PhaseState,
    phase_of_water,
    phase_of_air,
)
from .fluids import Fluid, FluidRegistry, fluids, WaterProperties, AirProperties

__version__ = "0.1.0"
__author__ = "ThermoUnits Contributors"
__license__ = "MIT"

__all__ = [
    "Quantity", "ureg", "UnitRegistry", "Dimension",
    "ThermodynamicState",
    "enthalpy_ideal_gas", "entropy_ideal_gas",
    "gibbs_free_energy", "helmholtz_free_energy",
    "internal_energy",
    "isentropic_temperature", "isentropic_pressure",
    "carnot_efficiency", "cop_heat_pump", "cop_refrigerator",
    "heat_of_vaporisation", "energy_balance",
    "PhaseState", "phase_of_water", "phase_of_air",
    "Fluid", "FluidRegistry", "fluids",
    "WaterProperties", "AirProperties",
    "__version__",
]
