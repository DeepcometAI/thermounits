"""
thermounits.units.registry
==========================
Central registry of unit definitions and conversion factors.

All values are stored in SI base units internally.  The registry maps
unit strings to (dimension, to_si_factor, to_si_offset) triples where:

    SI_value = raw_value * to_si_factor + to_si_offset

Offset is non-zero only for temperature scales (°C, °F).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .dimensions import (
    Dimension,
    DIMENSIONLESS,
    MASS, LENGTH, TIME, TEMPERATURE, AMOUNT,
    AREA, VOLUME,
    FORCE, PRESSURE, ENERGY, POWER,
    SPECIFIC_ENERGY, SPECIFIC_ENTROPY,
    MOLAR_ENERGY, MOLAR_ENTROPY,
    HEAT_CAPACITY, SPEC_HEAT_CAPACITY,
    DENSITY, DYNAMIC_VISCOSITY, THERMAL_CONDUCTIVITY,
)
from .quantity import Quantity, DimensionError


@dataclass(frozen=True)
class UnitDef:
    """Definition of a single unit in the registry."""
    dimension: Dimension
    to_si: float        # multiplicative factor:  val_si = val_unit * to_si + offset_si
    offset_si: float = 0.0  # additive offset (used for temperature scales)
    description: str = ""


class UnitRegistry:
    """
    Manages unit definitions and Quantity construction.

    Usage
    -----
    >>> from thermounits.units import ureg
    >>> T = ureg.quantity(25, "°C")   # 25 degrees Celsius
    >>> T.to("K")
    298.15 K
    >>> P = ureg.quantity(1, "atm")
    >>> P.to("Pa")
    101325.0 Pa
    """

    def __init__(self) -> None:
        self._units: Dict[str, UnitDef] = {}
        self._register_defaults()

    # ------------------------------------------------------------------
    # Registration API
    # ------------------------------------------------------------------

    def register(
        self,
        symbol: str,
        dimension: Dimension,
        to_si: float,
        offset_si: float = 0.0,
        description: str = "",
        aliases: Optional[Tuple[str, ...]] = None,
    ) -> None:
        """Register a unit symbol (and optional aliases) in the registry."""
        defn = UnitDef(dimension, to_si, offset_si, description)
        self._units[symbol] = defn
        if aliases:
            for alias in aliases:
                self._units[alias] = defn

    # ------------------------------------------------------------------
    # Quantity factory
    # ------------------------------------------------------------------

    def quantity(self, value: float, unit: str) -> Quantity:
        """
        Create a unit-safe Quantity from a raw numeric value and unit string.

        Parameters
        ----------
        value : float
            Numeric magnitude in the given *unit*.
        unit : str
            Unit symbol registered in this registry (e.g. ``"kJ/kg"``,
            ``"°C"``, ``"atm"``).

        Returns
        -------
        Quantity
            Value stored internally in SI base units.

        Raises
        ------
        KeyError
            If *unit* is not in the registry.
        """
        defn = self._lookup(unit)
        si_value = value * defn.to_si + defn.offset_si
        return Quantity(si_value, defn.dimension, unit)

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def convert(self, qty: Quantity, target_unit: str) -> Quantity:
        """
        Convert *qty* to *target_unit*.

        Raises
        ------
        DimensionError
            If *qty* and *target_unit* have incompatible dimensions.
        KeyError
            If *target_unit* is not registered.
        """
        defn = self._lookup(target_unit)
        if qty.dimension != defn.dimension:
            raise DimensionError(
                f"Cannot convert {qty.dimension!r} to '{target_unit}' "
                f"({defn.dimension!r}) — incompatible dimensions."
            )
        # Reverse the target unit's conversion:
        #   si = raw * to_si + offset  →  raw = (si - offset) / to_si
        raw = (qty.value - defn.offset_si) / defn.to_si
        return Quantity(raw, defn.dimension, target_unit)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def units_for_dimension(self, dim: Dimension) -> list:
        """Return all registered unit symbols that match *dim*."""
        return [sym for sym, d in self._units.items() if d.dimension == dim]

    def describe(self, unit: str) -> str:
        """Return a human-readable description of *unit*."""
        defn = self._lookup(unit)
        return (
            f"{unit}: {defn.description or '(no description)'}\n"
            f"  Dimension : {defn.dimension!r}\n"
            f"  SI factor : {defn.to_si}"
            + (f"  SI offset : {defn.offset_si}" if defn.offset_si else "")
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _lookup(self, unit: str) -> UnitDef:
        try:
            return self._units[unit]
        except KeyError:
            close = [u for u in self._units if unit.lower() in u.lower()]
            hint = f"  Did you mean: {', '.join(close[:5])}" if close else ""
            raise KeyError(f"Unknown unit: '{unit}'.{hint}") from None

    # ------------------------------------------------------------------
    # Default unit registrations
    # ------------------------------------------------------------------

    def _register_defaults(self) -> None:
        R = self.register

        # ── Temperature ────────────────────────────────────────────────
        R("K",   TEMPERATURE, 1.0,          0.0,     "Kelvin (SI base)")
        R("°C",  TEMPERATURE, 1.0,          273.15,  "Celsius",   aliases=("degC", "celsius", "C"))
        R("°F",  TEMPERATURE, 5/9,          273.15 - 32*5/9, "Fahrenheit", aliases=("degF", "fahrenheit", "F"))
        R("°R",  TEMPERATURE, 5/9,          0.0,     "Rankine",   aliases=("degR", "R", "rankine"))

        # ── Mass ───────────────────────────────────────────────────────
        R("kg",  MASS,  1.0,        0.0, "Kilogram (SI base)")
        R("g",   MASS,  1e-3,       0.0, "Gram",         aliases=("gram",))
        R("mg",  MASS,  1e-6,       0.0, "Milligram")
        R("lb",  MASS,  0.45359237, 0.0, "Pound-mass",   aliases=("lbm", "pound"))
        R("oz",  MASS,  0.0283495,  0.0, "Ounce")
        R("ton", MASS,  907.18474,  0.0, "Short ton (US)")
        R("tonne", MASS, 1000.0,   0.0, "Metric tonne")

        # ── Length ─────────────────────────────────────────────────────
        R("m",   LENGTH, 1.0,      0.0, "Metre (SI base)")
        R("cm",  LENGTH, 1e-2,     0.0, "Centimetre")
        R("mm",  LENGTH, 1e-3,     0.0, "Millimetre")
        R("km",  LENGTH, 1e3,      0.0, "Kilometre")
        R("ft",  LENGTH, 0.3048,   0.0, "Foot",  aliases=("feet",))
        R("in",  LENGTH, 0.0254,   0.0, "Inch",  aliases=("inch",))
        R("mi",  LENGTH, 1609.344, 0.0, "Mile")

        # ── Pressure ───────────────────────────────────────────────────
        R("Pa",   PRESSURE, 1.0,          0.0, "Pascal (SI base)")
        R("kPa",  PRESSURE, 1e3,          0.0, "Kilopascal")
        R("MPa",  PRESSURE, 1e6,          0.0, "Megapascal")
        R("bar",  PRESSURE, 1e5,          0.0, "Bar",          aliases=("Bar",))
        R("mbar", PRESSURE, 100.0,        0.0, "Millibar")
        R("atm",  PRESSURE, 101325.0,     0.0, "Standard atmosphere")
        R("psi",  PRESSURE, 6894.757,     0.0, "Pound-force per square inch")
        R("torr", PRESSURE, 133.322,      0.0, "Torr (mmHg)")
        R("mmHg", PRESSURE, 133.322,      0.0, "Millimetre of mercury")
        R("inHg", PRESSURE, 3386.39,      0.0, "Inch of mercury")

        # ── Energy ─────────────────────────────────────────────────────
        R("J",    ENERGY, 1.0,       0.0, "Joule (SI base)")
        R("kJ",   ENERGY, 1e3,       0.0, "Kilojoule")
        R("MJ",   ENERGY, 1e6,       0.0, "Megajoule")
        R("GJ",   ENERGY, 1e9,       0.0, "Gigajoule")
        R("cal",  ENERGY, 4.184,     0.0, "Thermochemical calorie")
        R("kcal", ENERGY, 4184.0,    0.0, "Kilocalorie")
        R("BTU",  ENERGY, 1055.06,   0.0, "British Thermal Unit", aliases=("Btu", "btu"))
        R("kBTU", ENERGY, 1055060.0, 0.0, "Kilo-BTU")
        R("Wh",   ENERGY, 3600.0,    0.0, "Watt-hour")
        R("kWh",  ENERGY, 3.6e6,     0.0, "Kilowatt-hour")
        R("MWh",  ENERGY, 3.6e9,     0.0, "Megawatt-hour")
        R("therm",ENERGY, 1.05506e8, 0.0, "Therm (US)")
        R("eV",   ENERGY, 1.602176634e-19, 0.0, "Electronvolt")

        # ── Power ──────────────────────────────────────────────────────
        R("W",    POWER, 1.0,    0.0, "Watt (SI base)")
        R("kW",   POWER, 1e3,    0.0, "Kilowatt")
        R("MW",   POWER, 1e6,    0.0, "Megawatt")
        R("GW",   POWER, 1e9,    0.0, "Gigawatt")
        R("hp",   POWER, 745.7,  0.0, "Horsepower (mechanical)")
        R("BTU/h",POWER, 0.29307, 0.0,"BTU per hour", aliases=("Btu/h",))
        R("ton_refrig", POWER, 3516.853, 0.0, "Ton of refrigeration")

        # ── Specific energy (J/kg) ─────────────────────────────────────
        R("J/kg",    SPECIFIC_ENERGY, 1.0,    0.0, "Joule per kilogram")
        R("kJ/kg",   SPECIFIC_ENERGY, 1e3,    0.0, "Kilojoule per kilogram")
        R("MJ/kg",   SPECIFIC_ENERGY, 1e6,    0.0, "Megajoule per kilogram")
        R("BTU/lb",  SPECIFIC_ENERGY, 2326.0, 0.0, "BTU per pound-mass")
        R("cal/g",   SPECIFIC_ENERGY, 4184.0, 0.0, "Calorie per gram")
        R("kcal/kg", SPECIFIC_ENERGY, 4184.0, 0.0, "Kilocalorie per kilogram")

        # ── Specific entropy / specific heat [J/(kg·K)] ────────────────
        R("J/(kg·K)",    SPECIFIC_ENTROPY, 1.0,          0.0, "Joule per kilogram-kelvin")
        R("kJ/(kg·K)",   SPECIFIC_ENTROPY, 1e3,          0.0, "Kilojoule per kilogram-kelvin")
        R("BTU/(lb·°R)", SPECIFIC_ENTROPY, 4186.8,       0.0, "BTU per pound-rankine")
        R("BTU/(lb·°F)", SPECIFIC_ENTROPY, 4186.8,       0.0, "BTU per pound-fahrenheit")
        R("cal/(g·K)",   SPECIFIC_ENTROPY, 4184.0,       0.0, "Calorie per gram-kelvin")

        # ── Volume ─────────────────────────────────────────────────────
        R("m³",   VOLUME, 1.0,       0.0, "Cubic metre")
        R("L",    VOLUME, 1e-3,      0.0, "Litre",        aliases=("l", "liter"))
        R("mL",   VOLUME, 1e-6,      0.0, "Millilitre",   aliases=("ml",))
        R("cm³",  VOLUME, 1e-6,      0.0, "Cubic centimetre")
        R("ft³",  VOLUME, 0.0283168, 0.0, "Cubic foot")
        R("in³",  VOLUME, 1.6387e-5, 0.0, "Cubic inch")
        R("gal",  VOLUME, 0.003785,  0.0, "US gallon",    aliases=("US_gal",))
        R("imperial_gal", VOLUME, 0.004546, 0.0, "Imperial gallon")

        # ── Density ────────────────────────────────────────────────────
        R("kg/m³",  DENSITY, 1.0,      0.0, "Kilogram per cubic metre")
        R("g/cm³",  DENSITY, 1000.0,   0.0, "Gram per cubic centimetre")
        R("lb/ft³", DENSITY, 16.0185,  0.0, "Pound per cubic foot")
        R("lb/in³", DENSITY, 27679.9,  0.0, "Pound per cubic inch")

        # ── Molar quantities ───────────────────────────────────────────
        R("J/mol",     MOLAR_ENERGY,  1.0,  0.0, "Joule per mole")
        R("kJ/mol",    MOLAR_ENERGY,  1e3,  0.0, "Kilojoule per mole")
        R("kcal/mol",  MOLAR_ENERGY,  4184.0, 0.0, "Kilocalorie per mole")
        R("J/(mol·K)", MOLAR_ENTROPY, 1.0,  0.0, "Joule per mole-kelvin")

        # ── Thermal conductivity  [W/(m·K)] ────────────────────────────
        R("W/(m·K)",     THERMAL_CONDUCTIVITY, 1.0,    0.0, "Watt per metre-kelvin")
        R("BTU/(h·ft·°F)",THERMAL_CONDUCTIVITY, 1.7307, 0.0,"BTU per hour-foot-fahrenheit")

        # ── Time ───────────────────────────────────────────────────────
        R("s",   TIME, 1.0,    0.0, "Second (SI base)", aliases=("sec",))
        R("min", TIME, 60.0,   0.0, "Minute")
        R("h",   TIME, 3600.0, 0.0, "Hour",   aliases=("hr", "hour"))
        R("d",   TIME, 86400.0,0.0, "Day",    aliases=("day",))

        # ── Dimensionless ──────────────────────────────────────────────
        R("1",   DIMENSIONLESS, 1.0, 0.0, "Dimensionless")
        R("%",   DIMENSIONLESS, 0.01,0.0, "Percent")


# Singleton registry — import and use directly
ureg = UnitRegistry()
