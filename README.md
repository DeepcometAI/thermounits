# thermounits

**Unit-safe thermodynamics and heat transfer computations for Python.**

`thermounits` is an open-source, pure-Python library that makes thermodynamic calculations safe, reproducible, and ergonomic. Every quantity carries its physical dimension — dimensional mismatches raise immediately rather than silently producing wrong answers.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/thermounits)](https://pypi.org/project/thermounits/)

---

## Why thermounits?

Most thermodynamics libraries are either academic (hard to install, dense APIs) or proprietary. `thermounits` is:

- **Unit-safe** — every value is a `Quantity` with a checked physical dimension.
- **CLI-first** — instant results from the terminal; no script required.
- **Deterministic** — no hidden state, no random seeds, no side effects.
- **Zero dependencies** — pure Python stdlib only.
- **Open source** — MIT licence.

---

## Installation

```bash
pip install thermounits
```

---

## CLI Quick-Start

```bash
# Unit conversion
thermounits convert 100 degC K
thermounits convert 1 atm kPa
thermounits convert 2500 kJ/kg BTU/lb

# Water / steam state properties
thermounits steam --temp 200 --temp-unit degC --pressure 1 --pressure-unit MPa

# Dry-air ideal-gas properties
thermounits air --temp 25 --temp-unit degC

# Isentropic compression (γ = 1.4 by default)
thermounits isentropic --T1 300 --P1 100 --P2 500 --gamma 1.4

# Polytropic process
thermounits polytropic --T1 300 --P1 100 --P2 500 --n 1.3

# Carnot efficiency and COP
thermounits carnot --T-hot 800 --T-cold 300

# Gibbs free energy  g = h – Ts
thermounits gibbs --enthalpy 2500 --temp 400 --entropy 6.7

# Phase classification
thermounits phase water --temp 100 --temp-unit degC --pressure 101325

# Saturation table at temperature or pressure
thermounits saturation --temp 100 --temp-unit degC
thermounits saturation --pressure 500000

# List all built-in fluids
thermounits fluids
```

### Example output — `thermounits steam`

```
  ────────────────────────────────────────────────────────
  Water / Steam  |  T=473.15 K (200.0 °C)  |  P=1000.0 kPa
  ────────────────────────────────────────────────────────
  Phase                          superheated vapour
  Temperature                                473.15  K   (200.0 °C)
  Pressure                                1000000.0  Pa   (1000.0 kPa)
  Enthalpy h                                2810.81  kJ/kg
  Entropy  s                                 6.5075  kJ/(kg·K)
  Density  ρ                                 4.5794  kg/m³
  ────────────────────────────────────────────────────────
```

### Example output — `thermounits carnot --T-hot 800 --T-cold 300`

```
  ────────────────────────────────────────────────────────
  Carnot Cycle Analysis
  ────────────────────────────────────────────────────────
  T_hot                                         800  K   (526.85 °C)
  T_cold                                        300  K   (26.85 °C)
  η  Carnot efficiency           0.625000
  η  [%]                         62.5000
  COP_refrigerator               0.600000
  COP_heat_pump                  1.600000
  ────────────────────────────────────────────────────────
```

---

## Python API

### Unit-safe quantities

```python
from thermounits.units import ureg

T = ureg.quantity(25, "°C")      # stored internally as 298.15 K
P = ureg.quantity(1,  "atm")     # stored as 101325.0 Pa

print(T.to("K"))           # 298.15 K
print(P.to("kPa"))         # 101.325 kPa
print(T.magnitude_in("°F"))  # 77.0

# Dimension mismatch raises immediately — no silent wrong answers
T + P   # DimensionError: cannot add TEMPERATURE and PRESSURE
```

### Steam / water properties

```python
from thermounits.units import ureg
from thermounits.fluids import WaterProperties

wp = WaterProperties()

state = wp.at_T_P(
    ureg.quantity(200, "°C"),
    ureg.quantity(1,   "MPa"),
)
print(state.enthalpy.to("kJ/kg"))   # 2810 kJ/kg
print(state.phase.value)            # "superheated vapour"

# Full saturation table
props = wp.saturation_at_T(ureg.quantity(100, "°C"))
print(props["h_vap"].to("kJ/kg"))      # latent heat ≈ 2222 kJ/kg
print(props["pressure"].to("kPa"))    # ≈ 101.4 kPa
```

### Thermodynamic functions

```python
from thermounits import (
    isentropic_temperature,
    carnot_efficiency, cop_heat_pump, cop_refrigerator,
    gibbs_free_energy, energy_balance,
)

# Isentropic compression
T2 = isentropic_temperature(
    ureg.quantity(300, "K"),
    ureg.quantity(100, "kPa"),
    ureg.quantity(500, "kPa"),
    gamma=1.4,
)
print(T2.to("°C"))   # ≈ 202 °C

# Carnot analysis
Th = ureg.quantity(800, "K")
Tc = ureg.quantity(300, "K")
print(carnot_efficiency(Th, Tc))   # 0.625
print(cop_heat_pump(Th, Tc))       # 1.6

# Gibbs free energy
g = gibbs_free_energy(
    enthalpy    = ureg.quantity(2500, "kJ/kg"),
    temperature = ureg.quantity(400,  "K"),
    entropy     = ureg.quantity(6.7,  "kJ/(kg·K)"),
)
print(g.to("kJ/kg"))

# First-law energy balance (residual ≈ 0 for balanced system)
residual = energy_balance(
    q_in    = ureg.quantity(500, "kJ/kg"),
    w_out   = ureg.quantity(200, "kJ/kg"),
    delta_h = ureg.quantity(300, "kJ/kg"),
)
print(residual.value)   # 0.0
```

---

## Supported Units (80+)

| Category | Units |
|---|---|
| Temperature | K, °C (degC), °F (degF), °R (degR) |
| Pressure | Pa, kPa, MPa, bar, atm, psi, torr, mmHg, inHg |
| Energy | J, kJ, MJ, GJ, BTU (Btu), kWh, MWh, cal, kcal, therm, eV |
| Specific energy | J/kg, kJ/kg, MJ/kg, BTU/lb, cal/g, kcal/kg |
| Specific entropy / Cp | J/(kg·K), kJ/(kg·K), BTU/(lb·°R), BTU/(lb·°F) |
| Power | W, kW, MW, GW, hp, BTU/h, ton_refrig |
| Mass | kg, g, mg, lb, oz, ton, tonne |
| Volume | m³, L, mL, cm³, ft³, gal |
| Density | kg/m³, g/cm³, lb/ft³, lb/in³ |
| Time | s, min, h, d |

---

## Built-in Fluids

| Fluid | Formula | Model |
|---|---|---|
| water | H₂O | IAPWS-IF97 saturation curve, steam regions |
| air | N₂+O₂ | Ideal gas, NIST Shomate Cp(T) |
| nitrogen | N₂ | Ideal gas |
| oxygen | O₂ | Ideal gas |
| co2 | CO₂ | Ideal gas |
| hydrogen | H₂ | Ideal gas |
| argon | Ar | Ideal gas |

---

## Running Tests

```bash
git clone https://github.com/DeepcometAI/thermounits
cd thermounits
pip install -e ".[dev]"
pytest tests/ -v
# 43 passed in 0.36s
```

---

## Roadmap

- [ ] v0.2 — Refrigerant database (R134a, R410a, R32)
- [ ] v0.3 — Heat exchanger NTU-effectiveness method
- [ ] v0.4 — Psychrometrics (moist air)
- [ ] v0.5 — Full IAPWS-IF97 Regions 1–5
- [ ] v1.0 — User-extensible custom fluid registration via TOML

---

## Licence

MIT — see [LICENSE](LICENSE).
