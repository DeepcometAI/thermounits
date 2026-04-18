"""
thermounits.thermo.state
========================
ThermodynamicState — a structured container for a fully-specified fluid
state point.  All fields are Quantity objects with physical dimension
checks enforced at construction time.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from ..units.quantity import Quantity
from ..units.dimensions import (
    TEMPERATURE, PRESSURE, SPECIFIC_ENERGY, SPECIFIC_ENTROPY,
    DENSITY, DIMENSIONLESS,
)
from ..units.registry import ureg
from .phase import PhaseState


def _check_dim(qty: Quantity, expected_dim, name: str) -> Quantity:
    if qty.dimension != expected_dim:
        raise TypeError(
            f"'{name}' has dimension {qty.dimension!r}, "
            f"expected {expected_dim!r}."
        )
    return qty


@dataclass
class ThermodynamicState:
    """
    A fully-specified thermodynamic state point.

    Parameters
    ----------
    temperature : Quantity[TEMPERATURE]
        Absolute temperature in Kelvin (internally).
    pressure : Quantity[PRESSURE]
        Absolute pressure in Pascal (internally).
    enthalpy : Quantity[SPECIFIC_ENERGY], optional
        Specific enthalpy h [J/kg].
    entropy : Quantity[SPECIFIC_ENTROPY], optional
        Specific entropy s [J/(kg·K)].
    internal_energy : Quantity[SPECIFIC_ENERGY], optional
        Specific internal energy u [J/kg].
    density : Quantity[DENSITY], optional
        Mass density ρ [kg/m³].
    quality : Quantity[DIMENSIONLESS], optional
        Vapour quality x ∈ [0, 1]; only defined in two-phase region.
    phase : PhaseState, optional
        Phase label determined from the fluid database.
    fluid : str
        Fluid identifier (default ``"ideal_gas"``).

    Examples
    --------
    >>> from thermounits.units import ureg
    >>> from thermounits.thermo import ThermodynamicState
    >>> state = ThermodynamicState(
    ...     temperature=ureg.quantity(300, "K"),
    ...     pressure=ureg.quantity(101325, "Pa"),
    ...     fluid="air",
    ... )
    """

    temperature: Quantity
    pressure: Quantity
    enthalpy: Optional[Quantity] = None
    entropy: Optional[Quantity] = None
    internal_energy: Optional[Quantity] = None
    density: Optional[Quantity] = None
    quality: Optional[Quantity] = None
    phase: Optional[PhaseState] = None
    fluid: str = "ideal_gas"

    def __post_init__(self) -> None:
        _check_dim(self.temperature, TEMPERATURE, "temperature")
        _check_dim(self.pressure, PRESSURE, "pressure")
        if self.enthalpy is not None:
            _check_dim(self.enthalpy, SPECIFIC_ENERGY, "enthalpy")
        if self.entropy is not None:
            _check_dim(self.entropy, SPECIFIC_ENTROPY, "entropy")
        if self.internal_energy is not None:
            _check_dim(self.internal_energy, SPECIFIC_ENERGY, "internal_energy")
        if self.density is not None:
            _check_dim(self.density, DENSITY, "density")
        if self.quality is not None:
            _check_dim(self.quality, DIMENSIONLESS, "quality")
            q = self.quality.value
            if not (0.0 <= q <= 1.0):
                raise ValueError(
                    f"Vapour quality must be in [0, 1], got {q:.4f}."
                )
        if self.temperature.value <= 0:
            raise ValueError(
                f"Temperature must be > 0 K, got {self.temperature.value:.4f} K. "
                "Check for a Celsius/Kelvin confusion."
            )
        if self.pressure.value <= 0:
            raise ValueError(
                f"Pressure must be > 0 Pa, got {self.pressure.value:.4f} Pa."
            )

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    @property
    def T(self) -> Quantity:
        """Temperature (alias)."""
        return self.temperature

    @property
    def P(self) -> Quantity:
        """Pressure (alias)."""
        return self.pressure

    @property
    def h(self) -> Optional[Quantity]:
        """Specific enthalpy (alias)."""
        return self.enthalpy

    @property
    def s(self) -> Optional[Quantity]:
        """Specific entropy (alias)."""
        return self.entropy

    @property
    def u(self) -> Optional[Quantity]:
        """Specific internal energy (alias)."""
        return self.internal_energy

    @property
    def rho(self) -> Optional[Quantity]:
        """Density (alias)."""
        return self.density

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lines = [
            f"ThermodynamicState  [{self.fluid}]",
            f"  Temperature : {self.temperature.to('K')}   ({self.temperature.to('°C')})",
            f"  Pressure    : {self.pressure.to('Pa')}   ({self.pressure.to('kPa')})",
        ]
        if self.enthalpy is not None:
            lines.append(f"  Enthalpy    : {self.enthalpy.to('kJ/kg')}")
        if self.entropy is not None:
            lines.append(f"  Entropy     : {self.entropy.to('kJ/(kg·K)')}")
        if self.internal_energy is not None:
            lines.append(f"  Int. Energy : {self.internal_energy.to('kJ/kg')}")
        if self.density is not None:
            lines.append(f"  Density     : {self.density.to('kg/m³')}")
        if self.quality is not None:
            lines.append(f"  Quality     : {self.quality.value:.4f}")
        if self.phase is not None:
            lines.append(f"  Phase       : {self.phase.value}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"ThermodynamicState(T={self.temperature!r}, "
            f"P={self.pressure!r}, fluid={self.fluid!r})"
        )

    def to_dict(self) -> dict:
        """Serialise state to a plain dictionary (values in SI units)."""
        d = {
            "fluid": self.fluid,
            "temperature_K": self.temperature.value,
            "pressure_Pa": self.pressure.value,
        }
        if self.enthalpy is not None:
            d["enthalpy_J_kg"] = self.enthalpy.value
        if self.entropy is not None:
            d["entropy_J_kgK"] = self.entropy.value
        if self.internal_energy is not None:
            d["internal_energy_J_kg"] = self.internal_energy.value
        if self.density is not None:
            d["density_kg_m3"] = self.density.value
        if self.quality is not None:
            d["quality"] = self.quality.value
        if self.phase is not None:
            d["phase"] = self.phase.value
        return d
