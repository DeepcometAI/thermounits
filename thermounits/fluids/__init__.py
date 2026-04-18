"""
thermounits.fluids
==================
Built-in fluid property database.

Supported fluids (v1.0)
-----------------------
* water   — IAPWS-IF97 saturation properties + steam tables approximation
* air     — ideal gas (Cp, Cv, γ, M, μ, λ)
* nitrogen (N2), oxygen (O2), CO2, hydrogen (H2), argon (Ar)
            — ideal gas models
"""

from .fluid import Fluid, FluidRegistry, fluids
from .water import WaterProperties
from .air import AirProperties

__all__ = ["Fluid", "FluidRegistry", "fluids", "WaterProperties", "AirProperties"]
