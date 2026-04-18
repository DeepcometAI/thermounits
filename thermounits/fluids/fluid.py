"""
thermounits.fluids.fluid
========================
Base Fluid dataclass and the global FluidRegistry.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Fluid:
    """
    Static thermophysical properties of a pure substance.

    All values are in SI units.

    Parameters
    ----------
    name : str
        Canonical identifier (lower-case, no spaces).
    formula : str
        Chemical formula.
    molar_mass : float
        Molar mass [kg/mol].
    T_crit : float
        Critical temperature [K].
    P_crit : float
        Critical pressure [Pa].
    T_triple : float
        Triple point temperature [K].
    P_triple : float
        Triple point pressure [Pa].
    T_boil : float
        Normal boiling point at 101 325 Pa [K].
    cp_gas : float
        Specific heat at constant pressure (ideal gas, 298 K) [J/(kg·K)].
    cv_gas : float
        Specific heat at constant volume (ideal gas, 298 K) [J/(kg·K)].
    gamma : float
        Heat capacity ratio Cp/Cv.
    R_specific : float
        Specific gas constant R/M [J/(kg·K)].
    h_vap_boil : float
        Latent heat of vaporisation at T_boil [J/kg].
    description : str
        Human-readable description.
    aliases : tuple[str, ...]
        Alternative identifiers accepted by the registry.
    """

    name: str
    formula: str
    molar_mass: float       # kg/mol
    T_crit: float           # K
    P_crit: float           # Pa
    T_triple: float         # K
    P_triple: float         # Pa
    T_boil: float           # K
    cp_gas: float           # J/(kg·K)
    cv_gas: float           # J/(kg·K)
    gamma: float            # Cp/Cv
    R_specific: float       # J/(kg·K)
    h_vap_boil: float       # J/kg
    description: str = ""
    aliases: tuple = ()


class FluidRegistry:
    """Look-up registry for built-in and user-registered fluids."""

    def __init__(self) -> None:
        self._db: Dict[str, Fluid] = {}

    def register(self, fluid: Fluid) -> None:
        self._db[fluid.name] = fluid
        for alias in fluid.aliases:
            self._db[alias.lower()] = fluid

    def get(self, name: str) -> Fluid:
        key = name.lower().strip()
        if key not in self._db:
            available = ", ".join(sorted(set(f.name for f in self._db.values())))
            raise KeyError(
                f"Unknown fluid '{name}'. "
                f"Available fluids: {available}"
            )
        return self._db[key]

    def list_fluids(self) -> list:
        return sorted({f.name for f in self._db.values()})

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._db


# ---------------------------------------------------------------------------
# Universal gas constant
# ---------------------------------------------------------------------------
R_UNIVERSAL = 8.314462618   # J/(mol·K)


def _make_ideal_gas(
    name: str,
    formula: str,
    molar_mass_g_mol: float,
    T_crit: float,
    P_crit: float,
    T_triple: float,
    P_triple: float,
    T_boil: float,
    cp_J_kgK: float,
    h_vap_J_kg: float,
    description: str = "",
    aliases: tuple = (),
) -> Fluid:
    M = molar_mass_g_mol / 1000  # g/mol → kg/mol
    R_s = R_UNIVERSAL / M
    cv = cp_J_kgK - R_s
    gamma = cp_J_kgK / cv
    return Fluid(
        name=name,
        formula=formula,
        molar_mass=M,
        T_crit=T_crit,
        P_crit=P_crit,
        T_triple=T_triple,
        P_triple=P_triple,
        T_boil=T_boil,
        cp_gas=cp_J_kgK,
        cv_gas=cv,
        gamma=gamma,
        R_specific=R_s,
        h_vap_boil=h_vap_J_kg,
        description=description,
        aliases=aliases,
    )


# ---------------------------------------------------------------------------
# Built-in fluid definitions
# ---------------------------------------------------------------------------

_WATER = _make_ideal_gas(
    name="water",
    formula="H₂O",
    molar_mass_g_mol=18.01528,
    T_crit=647.096,
    P_crit=22.064e6,
    T_triple=273.16,
    P_triple=611.657,
    T_boil=373.124,
    cp_J_kgK=2080.0,     # steam at 100°C, 1 atm
    h_vap_J_kg=2_256_400.0,  # at 100°C
    description="Water / steam (H₂O)",
    aliases=("h2o", "steam", "H2O"),
)

_AIR = _make_ideal_gas(
    name="air",
    formula="N₂+O₂ (dry)",
    molar_mass_g_mol=28.9647,
    T_crit=132.5,
    P_crit=3.766e6,
    T_triple=59.75,
    P_triple=5930.0,
    T_boil=78.8,
    cp_J_kgK=1005.0,
    h_vap_J_kg=0.0,   # not applicable as idealgas
    description="Dry air (ideal-gas mixture)",
    aliases=("Air", "dry_air"),
)

_NITROGEN = _make_ideal_gas(
    name="nitrogen",
    formula="N₂",
    molar_mass_g_mol=28.014,
    T_crit=126.192,
    P_crit=3.3958e6,
    T_triple=63.151,
    P_triple=12_520.0,
    T_boil=77.355,
    cp_J_kgK=1040.0,
    h_vap_J_kg=199_200.0,
    description="Nitrogen (N₂)",
    aliases=("n2", "N2"),
)

_OXYGEN = _make_ideal_gas(
    name="oxygen",
    formula="O₂",
    molar_mass_g_mol=31.998,
    T_crit=154.581,
    P_crit=5.0430e6,
    T_triple=54.361,
    P_triple=146.33,
    T_boil=90.188,
    cp_J_kgK=919.0,
    h_vap_J_kg=213_200.0,
    description="Oxygen (O₂)",
    aliases=("o2", "O2"),
)

_CO2 = _make_ideal_gas(
    name="co2",
    formula="CO₂",
    molar_mass_g_mol=44.010,
    T_crit=304.128,
    P_crit=7.3773e6,
    T_triple=216.592,
    P_triple=517_950.0,
    T_boil=194.686,   # sublimation point at 1 atm
    cp_J_kgK=844.0,
    h_vap_J_kg=571_000.0,  # sublimation enthalpy
    description="Carbon dioxide (CO₂)",
    aliases=("carbon_dioxide", "CO2", "carbon dioxide"),
)

_HYDROGEN = _make_ideal_gas(
    name="hydrogen",
    formula="H₂",
    molar_mass_g_mol=2.01588,
    T_crit=33.145,
    P_crit=1.2964e6,
    T_triple=13.8033,
    P_triple=7_042.0,
    T_boil=20.271,
    cp_J_kgK=14_307.0,
    h_vap_J_kg=455_600.0,
    description="Hydrogen (H₂)",
    aliases=("h2", "H2"),
)

_ARGON = _make_ideal_gas(
    name="argon",
    formula="Ar",
    molar_mass_g_mol=39.948,
    T_crit=150.687,
    P_crit=4.8630e6,
    T_triple=83.8058,
    P_triple=68_891.0,
    T_boil=87.302,
    cp_J_kgK=520.3,
    h_vap_J_kg=161_100.0,
    description="Argon (Ar)",
    aliases=("Ar",),
)

# Global singleton
fluids = FluidRegistry()
for _f in [_WATER, _AIR, _NITROGEN, _OXYGEN, _CO2, _HYDROGEN, _ARGON]:
    fluids.register(_f)
