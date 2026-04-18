# CLI Reference

The `thermounits` CLI is exposed through the `thermounits` command.

## Global Help

```bash
thermounits --help
```

## Commands

## `convert`

Convert a value between compatible units.

```bash
thermounits convert <value> <from_unit> <to_unit>
```

Examples:

```bash
thermounits convert 100 degC K
thermounits convert 1 atm kPa
thermounits convert 2500 kJ/kg BTU/lb
```

## `steam`

Compute water/steam state at temperature and pressure.

```bash
thermounits steam --temp <value> --temp-unit <unit> --pressure <value> --pressure-unit <unit>
```

Example:

```bash
thermounits steam --temp 200 --temp-unit degC --pressure 1 --pressure-unit MPa
```

Returns phase, temperature, pressure, enthalpy, entropy, and density.

## `air`

Compute dry-air ideal-gas properties at temperature and pressure.

```bash
thermounits air --temp <value> --temp-unit <unit> [--pressure <value> --pressure-unit <unit>]
```

Defaults:

- pressure = `101325 Pa`
- pressure unit = `Pa`

Example:

```bash
thermounits air --temp 25 --temp-unit degC
```

Returns enthalpy, entropy, density, Cp, Cv, gamma, and speed of sound.

## `isentropic`

Ideal-gas isentropic temperature relation:

```text
T2 = T1 * (P2/P1)^((gamma-1)/gamma)
```

Usage:

```bash
thermounits isentropic --T1 <value> --P1 <value> --P2 <value> [--gamma 1.4] [--T-unit K] [--P-unit kPa]
```

Example:

```bash
thermounits isentropic --T1 300 --P1 100 --P2 500 --gamma 1.4
```

## `polytropic`

Polytropic temperature relation:

```text
T2 = T1 * (P2/P1)^((n-1)/n)
```

Usage:

```bash
thermounits polytropic --T1 <value> --P1 <value> --P2 <value> --n <value> [--T-unit K] [--P-unit kPa]
```

## `carnot`

Compute Carnot efficiency and COP values.

```bash
thermounits carnot --T-hot <value> --T-cold <value> [--T-unit K]
```

Example:

```bash
thermounits carnot --T-hot 800 --T-cold 300
```

## `gibbs`

Compute specific Gibbs free energy:

```text
g = h - T*s
```

Usage:

```bash
thermounits gibbs --enthalpy <kJ/kg> --temp <K> --entropy <kJ/(kg·K)>
```

## `phase`

Classify phase for supported fluids (`water`, `air`).

```bash
thermounits phase [fluid] --temp <value> --temp-unit <unit> --pressure <value> --pressure-unit <unit>
```

Example:

```bash
thermounits phase water --temp 100 --temp-unit degC --pressure 101325
```

## `saturation`

Water saturation properties at either temperature or pressure.

```bash
thermounits saturation --temp <value> [--temp-unit K]
thermounits saturation --pressure <value> [--pressure-unit Pa]
```

Examples:

```bash
thermounits saturation --temp 100 --temp-unit degC
thermounits saturation --pressure 500000
```

## `fluids`

List built-in fluid definitions.

```bash
thermounits fluids
```

## `version`

Show package version.

```bash
thermounits version
```

## Error Handling

- Unknown units return exit code `1`.
- Dimension mismatches return exit code `1`.
- Invalid thermodynamic state combinations return exit code `1`.
- `Ctrl+C` returns exit code `130`.
