# Python API Guide

## Import Surface

Most common imports:

```python
from thermounits.units import ureg
from thermounits import (
    isentropic_temperature,
    carnot_efficiency,
    gibbs_free_energy,
)
from thermounits.fluids import WaterProperties, AirProperties
```

## Units and Quantities

`Quantity` objects carry both numeric value and physical dimension.

```python
from thermounits.units import ureg

T = ureg.quantity(25, "degC")
P = ureg.quantity(1, "atm")

print(T.to("K"))      # 298.15 K
print(P.to("kPa"))    # 101.325 kPa
```

Dimension safety:

```python
T + P  # raises DimensionError
```

## Thermodynamic Functions

Functions are deterministic and dimension-checked.

### `isentropic_temperature(T1, P1, P2, gamma) -> Quantity`

```python
T2 = isentropic_temperature(
    ureg.quantity(300, "K"),
    ureg.quantity(100, "kPa"),
    ureg.quantity(500, "kPa"),
    gamma=1.4,
)
```

### `gibbs_free_energy(h, T, s) -> Quantity`

```python
g = gibbs_free_energy(
    enthalpy=ureg.quantity(2500, "kJ/kg"),
    temperature=ureg.quantity(400, "K"),
    entropy=ureg.quantity(6.7, "kJ/(kg·K)"),
)
```

### Carnot helpers

- `carnot_efficiency(T_hot, T_cold) -> float`
- `cop_refrigerator(T_hot, T_cold) -> float`
- `cop_heat_pump(T_hot, T_cold) -> float`

### First-law residual

`energy_balance(q_in, w_out, delta_h) -> Quantity`

Returns near-zero residual when balance is satisfied.

## Fluid Property APIs

## `WaterProperties`

```python
from thermounits.fluids import WaterProperties
from thermounits.units import ureg

wp = WaterProperties()

state = wp.at_T_P(
    ureg.quantity(200, "degC"),
    ureg.quantity(1, "MPa"),
)

print(state.phase.value)
print(state.enthalpy.to("kJ/kg"))
```

Saturation:

```python
sat = wp.saturation_at_T(ureg.quantity(100, "degC"))
print(sat["pressure"].to("kPa"))
print(sat["h_vap"].to("kJ/kg"))
```

## `AirProperties`

```python
from thermounits.fluids import AirProperties
from thermounits.units import ureg

ap = AirProperties()
state = ap.at_T_P(ureg.quantity(25, "degC"), ureg.quantity(101325, "Pa"))

cp = ap.cp(ureg.quantity(300, "K"))
gamma = ap.gamma(ureg.quantity(300, "K"))
```

## ThermodynamicState Container

`ThermodynamicState` bundles a fluid state with optional properties:

- temperature
- pressure
- enthalpy
- entropy
- internal energy
- density
- quality
- phase
- fluid name

The object validates dimensions and physical bounds (`T > 0`, `P > 0`) on construction.

## Supported Unit Categories

See `README.md` for full lists. Key families:

- temperature
- pressure
- energy and specific energy
- specific entropy / specific heat
- power
- mass and volume
- density
- time
