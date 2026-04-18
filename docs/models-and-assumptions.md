# Models and Assumptions

This document defines what physical models `thermounits` currently uses and where those models are valid.

## Philosophy

The package prioritizes:

- unit safety,
- deterministic behavior,
- practical engineering approximations,
- transparent formulas.

It does **not** currently target full real-fluid property fidelity across all thermodynamic regions.

## Water Model

### What is implemented

- Saturation pressure/temperature relations based on IF97 Region 4 style correlations.
- Phase logic across:
  - subcooled liquid,
  - two-phase boundary,
  - superheated vapor,
  - supercritical region.
- Saturation property helpers for enthalpy, entropy, and density via fitted/approximate relations.

### Important assumptions

- Subcooled liquid uses an incompressible-style pressure correction.
- Superheated vapor uses an ideal-gas-like approximation with reference anchoring.
- Two-phase property from `(T, P)` alone does not infer quality `x` without additional state information.

### Validity caveats

- Near-critical and extreme-condition behavior should be treated as approximate.
- Ice/solid-water region is out of scope.

## Air Model

### What is implemented

- Dry air modeled as ideal gas.
- Temperature-dependent Cp(T) from Shomate correlations.
- Cv(T), gamma(T), density, entropy, and speed of sound derived consistently from ideal-gas relations.

### Important assumptions

- Composition is fixed dry air.
- No humidity or condensable-water effects.
- No non-ideal gas corrections at high pressure.

## Additional Built-in Fluids

Fluids such as nitrogen, oxygen, CO2, hydrogen, and argon are represented through ideal-gas metadata in the fluid registry.

Current use is primarily:

- lookup/listing,
- static properties,
- baseline thermodynamic constants.

## Thermodynamic Function Assumptions

- Isentropic and polytropic helpers assume ideal-gas relations.
- Carnot efficiency/COP helpers assume absolute temperatures and reversible limits.
- Energy balance helper is a first-law residual utility, not a process simulator.

## Error and Safety Behavior

- Dimension mismatches raise immediately.
- Unsupported/invalid thermodynamic domains raise `ValueError`.
- Unknown units and unknown fluids raise clear lookup errors.

## Recommended Use Cases

- education and teaching,
- sanity checks and quick engineering calculations,
- script automation with strict unit safety,
- CLI-based fast calculations.

## Not Yet Recommended For

- high-accuracy steam-table replacement across all IF97 regions,
- cryogenic or near-critical research-grade property estimation,
- moist-air psychrometric calculations (not yet implemented).
