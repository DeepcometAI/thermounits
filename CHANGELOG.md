# Changelog

## [0.1.0] — 2024-01-01

### Added
- `Quantity` class with full arithmetic, comparison, and dimension safety
- `UnitRegistry` with 80+ units across SI and Imperial systems
- `Dimension` type encoding all 7 SI base dimensions
- `ThermodynamicState` dataclass for structured fluid state points
- Water phase classification via IAPWS-IF97 Region 4 saturation curve
- Air phase classification (ideal-gas permanent gas model)
- `WaterProperties`: saturation tables at T or P, state at (T,P)
- `AirProperties`: NIST Shomate Cp(T), density, γ, speed of sound
- Fluid registry with 7 built-in fluids: water, air, N2, O2, CO2, H2, Ar
- Thermodynamic functions: h, s, g, a, u (ideal gas)
- Isentropic and polytropic process relations
- Carnot efficiency, COP for refrigerator and heat pump
- First-law energy balance helper
- Clausius-Clapeyron equation
- Heat of vaporisation helper
- Isothermal and adiabatic work calculations
- CLI with 11 subcommands: convert, steam, air, isentropic, polytropic,
  carnot, gibbs, phase, saturation, fluids, version
