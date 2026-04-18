# Architecture

`thermounits` is organized into four primary layers:

## 1) `units` layer

Purpose: dimensional safety and unit conversion.

Main modules:

- `thermounits.units.dimensions`
- `thermounits.units.quantity`
- `thermounits.units.registry`

Responsibilities:

- represent physical dimensions as exponent vectors (`Dimension`)
- enforce dimension compatibility during arithmetic (`Quantity`)
- convert between user-facing units and SI-internal values (`UnitRegistry`)

Design notes:

- `Quantity` is immutable.
- Internal storage is SI.
- Temperature offset units (`degC`, `degF`) are handled via affine conversion.

## 2) `thermo` layer

Purpose: reusable thermodynamic equations and phase classification.

Main modules:

- `thermounits.thermo.functions`
- `thermounits.thermo.phase`
- `thermounits.thermo.state`

Responsibilities:

- provide deterministic ideal-gas and cycle relations
- classify phase behavior (`water`, `air`)
- represent state points (`ThermodynamicState`) with validation

Design notes:

- public functions accept and return `Quantity` where applicable
- invalid dimensions fail early with explicit messages

## 3) `fluids` layer

Purpose: fluid-specific models and databases.

Main modules:

- `thermounits.fluids.fluid`
- `thermounits.fluids.water`
- `thermounits.fluids.air`

Responsibilities:

- provide built-in fluid metadata (`FluidRegistry`)
- compute water properties from simplified IF97-based methods
- compute dry-air ideal-gas properties using Shomate Cp(T)

## 4) `cli` layer

Purpose: terminal-first access to all common calculations.

Main module:

- `thermounits.cli.main`

Responsibilities:

- parse command arguments
- route to thermodynamic calculations
- print structured, readable output
- provide deterministic exit codes and clear errors

## Package Boundaries and Flow

Typical data flow:

1. User provides value + unit (CLI or Python).
2. `UnitRegistry` converts input to SI-backed `Quantity`.
3. `thermo`/`fluids` compute with validated dimensions.
4. Results are returned as `Quantity`.
5. Output is formatted in requested display units.

## Testing Strategy

The test suite validates:

- quantity arithmetic and conversion correctness
- dimension mismatch behavior
- phase and saturation behavior for water
- ideal-gas air properties
- CLI execution and output sanity

Current baseline: `43` tests.
