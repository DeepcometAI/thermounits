"""
thermounits.cli.main
====================
Full CLI for thermounits with subcommands for all thermodynamic computations.
"""

from __future__ import annotations
import argparse
import sys
import textwrap

from ..units.registry import ureg
from ..units.quantity import DimensionError


def _header(title: str) -> None:
    print()
    print(f"  {'─' * 56}")
    print(f"  {title}")
    print(f"  {'─' * 56}")


def _row(label: str, qty, alt_unit=None) -> None:
    if qty is None:
        return
    from ..units.quantity import Quantity
    if isinstance(qty, (str, PhaseWrapper)):
        print(f"  {label:<30} {qty}")
        return
    if isinstance(qty, Quantity):
        main = f"{qty.value:>18.6g}  {qty.unit_label}"
        alt = ""
        if alt_unit:
            try:
                alt = f"   ({qty.to(alt_unit)})"
            except Exception:
                pass
        print(f"  {label:<30} {main}{alt}")


class PhaseWrapper:
    def __init__(self, v): self.v = v
    def __str__(self): return str(self.v)


def _row_float(label: str, value: float, fmt: str = ".6g") -> None:
    print(f"  {label:<30} {value:{fmt}}")


def _footer() -> None:
    print(f"  {'─' * 56}")
    print()


# ── convert ────────────────────────────────────────────────────────────────

def cmd_convert(args):
    try:
        qty = ureg.quantity(args.value, args.from_unit)
        result = qty.to(args.to_unit)
    except (KeyError, DimensionError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header("Unit Conversion")
    _row("Input", qty)
    _row("Output", result)
    _footer()
    return 0


# ── steam ──────────────────────────────────────────────────────────────────

def cmd_steam(args):
    from ..fluids.water import WaterProperties
    try:
        T = ureg.quantity(args.temp, args.temp_unit or "K")
        P = ureg.quantity(args.pressure, args.pressure_unit or "Pa")
        state = WaterProperties().at_T_P(T, P)
    except (KeyError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header(f"Water / Steam  |  T={T.to('K')} ({T.to('°C')})  |  P={P.to('kPa')}")
    _row("Phase",       state.phase.value if state.phase else "—")
    _row("Temperature", state.temperature.to("K"),         "°C")
    _row("Pressure",    state.pressure.to("Pa"),           "kPa")
    _row("Enthalpy h",  state.enthalpy.to("kJ/kg") if state.enthalpy else None)
    _row("Entropy  s",  state.entropy.to("kJ/(kg·K)") if state.entropy else None)
    _row("Density  ρ",  state.density.to("kg/m³") if state.density else None)
    if state.quality is not None:
        _row_float("Vapour quality x", state.quality.value, ".4f")
    _footer()
    return 0


# ── air ────────────────────────────────────────────────────────────────────

def cmd_air(args):
    from ..fluids.air import AirProperties
    try:
        T = ureg.quantity(args.temp, args.temp_unit or "K")
        P = ureg.quantity(args.pressure, args.pressure_unit or "Pa")
        ap = AirProperties()
        state   = ap.at_T_P(T, P)
        cp_qty  = ap.cp(T)
        cv_qty  = ap.cv(T)
        gamma   = ap.gamma(T)
        c_sound = ap.speed_of_sound(T)
    except (KeyError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header(f"Dry Air (ideal gas)  |  T={T.to('K')} ({T.to('°C')})  |  P={P.to('kPa')}")
    _row("Temperature",     state.temperature.to("K"),      "°C")
    _row("Pressure",        state.pressure.to("Pa"),        "kPa")
    _row("Enthalpy h",      state.enthalpy.to("kJ/kg"))
    _row("Entropy  s",      state.entropy.to("kJ/(kg·K)"))
    _row("Density  ρ",      state.density.to("kg/m³"))
    _row("Cp",              cp_qty.to("kJ/(kg·K)"))
    _row("Cv",              cv_qty.to("kJ/(kg·K)"))
    _row_float("γ = Cp/Cv", gamma, ".5f")
    _row("Speed of sound",  c_sound)
    _footer()
    return 0


# ── isentropic ─────────────────────────────────────────────────────────────

def cmd_isentropic(args):
    from ..thermo.functions import isentropic_temperature
    try:
        T1 = ureg.quantity(args.T1, args.T_unit or "K")
        P1 = ureg.quantity(args.P1, args.P_unit or "kPa")
        P2 = ureg.quantity(args.P2, args.P_unit or "kPa")
        T2 = isentropic_temperature(T1, P1, P2, args.gamma)
    except (KeyError, ValueError, DimensionError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header(f"Isentropic Process  (γ = {args.gamma})")
    _row("T₁  inlet temperature",  T1.to("K"), "°C")
    _row("P₁  inlet pressure",     P1.to("kPa"), "Pa")
    _row("P₂  exit pressure",      P2.to("kPa"), "Pa")
    _row_float("P₂/P₁  pressure ratio", P2.value / P1.value, ".4f")
    _row("T₂  exit temperature",   T2.to("K"), "°C")
    _row_float("ΔT = T₂ – T₁  [K]", T2.value - T1.value, ".4f")
    _footer()
    return 0


# ── polytropic ─────────────────────────────────────────────────────────────

def cmd_polytropic(args):
    from ..thermo.functions import polytropic_temperature
    try:
        T1 = ureg.quantity(args.T1, args.T_unit or "K")
        P1 = ureg.quantity(args.P1, args.P_unit or "kPa")
        P2 = ureg.quantity(args.P2, args.P_unit or "kPa")
        T2 = polytropic_temperature(T1, P1, P2, args.n)
    except (KeyError, ValueError, DimensionError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header(f"Polytropic Process  (n = {args.n})")
    _row("T₁  inlet temperature", T1.to("K"), "°C")
    _row("P₁  inlet pressure",    P1.to("kPa"), "Pa")
    _row("P₂  exit pressure",     P2.to("kPa"), "Pa")
    _row("T₂  exit temperature",  T2.to("K"), "°C")
    _row_float("ΔT  [K]", T2.value - T1.value, ".4f")
    _footer()
    return 0


# ── carnot ─────────────────────────────────────────────────────────────────

def cmd_carnot(args):
    from ..thermo.functions import carnot_efficiency, cop_refrigerator, cop_heat_pump
    try:
        Th = ureg.quantity(args.T_hot,  args.T_unit or "K")
        Tc = ureg.quantity(args.T_cold, args.T_unit or "K")
        eta    = carnot_efficiency(Th, Tc)
        cop_r  = cop_refrigerator(Th, Tc)
        cop_hp = cop_heat_pump(Th, Tc)
    except (KeyError, ValueError, DimensionError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header("Carnot Cycle Analysis")
    _row("T_hot",  Th.to("K"), "°C")
    _row("T_cold", Tc.to("K"), "°C")
    _row_float("η  Carnot efficiency",   eta,     ".6f")
    _row_float("η  [%]",                 eta*100, ".4f")
    _row_float("COP_refrigerator",       cop_r,   ".6f")
    _row_float("COP_heat_pump",          cop_hp,  ".6f")
    _footer()
    return 0


# ── gibbs ──────────────────────────────────────────────────────────────────

def cmd_gibbs(args):
    from ..thermo.functions import gibbs_free_energy
    from ..units.dimensions import SPECIFIC_ENERGY
    from ..units.quantity import Quantity
    try:
        h = ureg.quantity(args.enthalpy, "kJ/kg")
        T = ureg.quantity(args.temp, "K")
        s = ureg.quantity(args.entropy, "kJ/(kg·K)")
        g = gibbs_free_energy(h, T, s)
        ts = Quantity(T.value * s.value, SPECIFIC_ENERGY, "J/kg")
    except (KeyError, ValueError, DimensionError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header("Gibbs Free Energy   g = h – Ts")
    _row("Enthalpy h",    h.to("kJ/kg"))
    _row("Temperature T", T.to("K"), "°C")
    _row("Entropy s",     s.to("kJ/(kg·K)"))
    _row("Ts  [kJ/kg]",   ts.to("kJ/kg"))
    _row("g = h – Ts",    g.to("kJ/kg"))
    _footer()
    return 0


# ── phase ──────────────────────────────────────────────────────────────────

def cmd_phase(args):
    try:
        T = ureg.quantity(args.temp, args.temp_unit or "K")
        P = ureg.quantity(args.pressure, args.pressure_unit or "Pa")
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    fluid = (args.fluid or "water").lower()
    try:
        if fluid in ("water", "steam", "h2o"):
            from ..thermo.phase import phase_of_water, sat_pressure_water
            phase = phase_of_water(T.value, P.value)
            p_sat = sat_pressure_water(min(T.value, 647.09))
            extra = f"P_sat at T = {p_sat/1000:.4f} kPa"
        elif fluid in ("air", "dry_air"):
            from ..thermo.phase import phase_of_air
            phase = phase_of_air(T.value, P.value)
            extra = ""
        else:
            print(f"Error: no phase model for '{fluid}'.", file=sys.stderr); return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header(f"Phase Classification  [{fluid}]")
    _row("Temperature", T.to("K"), "°C")
    _row("Pressure",    P.to("Pa"), "kPa")
    print(f"  {'Phase':<30} {phase.value}")
    if extra:
        print(f"  {extra}")
    _footer()
    return 0


# ── saturation ─────────────────────────────────────────────────────────────

def cmd_saturation(args):
    from ..fluids.water import WaterProperties
    wp = WaterProperties()
    try:
        if args.temp is not None:
            T = ureg.quantity(args.temp, args.temp_unit or "K")
            props = wp.saturation_at_T(T)
            label = f"T = {T.to('K')}  ({T.to('°C')})"
        else:
            P = ureg.quantity(args.pressure, args.pressure_unit or "Pa")
            props = wp.saturation_at_P(P)
            label = f"P = {P.to('Pa')}  ({P.to('kPa')})"
    except (KeyError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr); return 1
    _header(f"Water Saturation Properties  @  {label}")
    if "temperature" in props:
        _row("T_sat",           props["temperature"].to("K"), "°C")
    if "pressure" in props:
        _row("P_sat",           props["pressure"].to("Pa"), "kPa")
    _row("h_f  (liquid)",       props["h_liquid"].to("kJ/kg"))
    _row("h_g  (vapour)",       props["h_vapour"].to("kJ/kg"))
    _row("h_fg (latent heat)",  props["h_vap"].to("kJ/kg"))
    _row("s_f  (liquid)",       props["s_liquid"].to("kJ/(kg·K)"))
    _row("s_g  (vapour)",       props["s_vapour"].to("kJ/(kg·K)"))
    _row("ρ_f  (liquid)",       props["density_liquid"].to("kg/m³"))
    _row("ρ_g  (vapour)",       props["density_vapour"].to("kg/m³"))
    _footer()
    return 0


# ── fluids ─────────────────────────────────────────────────────────────────

def cmd_fluids(_args):
    from ..fluids.fluid import fluids as _fluids
    _header("Built-in Fluids")
    for name in _fluids.list_fluids():
        f = _fluids.get(name)
        print(
            f"  {f.name:<14}  {f.formula:<14}  "
            f"M={f.molar_mass*1000:.4f} g/mol  "
            f"T_crit={f.T_crit:.2f} K  "
            f"P_crit={f.P_crit/1e6:.3f} MPa"
        )
    _footer()
    return 0


# ── version ────────────────────────────────────────────────────────────────

def cmd_version(_args):
    from .. import __version__
    print(f"thermounits {__version__}")
    return 0


# ── parser ─────────────────────────────────────────────────────────────────

def _build_parser():
    parser = argparse.ArgumentParser(
        prog="thermounits",
        description=textwrap.dedent("""\
            thermounits — unit-safe thermodynamics CLI

            Subcommands:
              convert     Unit conversion
              steam       Water / steam properties at (T, P)
              air         Dry-air ideal-gas properties at (T, P)
              isentropic  Isentropic exit temperature / pressure ratio
              polytropic  Polytropic exit temperature
              carnot      Carnot efficiency and COP
              gibbs       Gibbs free energy  g = h – Ts
              phase       Phase classification (water | air)
              saturation  Water saturation table at T or P
              fluids      List built-in fluids
              version     Print version

            Run 'thermounits <subcommand> --help' for per-command options.
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="<subcommand>")

    # convert
    p = sub.add_parser("convert", help="Convert between units")
    p.add_argument("value",     type=float)
    p.add_argument("from_unit", type=str)
    p.add_argument("to_unit",   type=str)

    # steam
    p = sub.add_parser("steam", help="Water/steam state at T and P")
    p.add_argument("--temp",          type=float, required=True)
    p.add_argument("--temp-unit",     type=str,   default="K",   dest="temp_unit")
    p.add_argument("--pressure",      type=float, required=True)
    p.add_argument("--pressure-unit", type=str,   default="Pa",  dest="pressure_unit")

    # air
    p = sub.add_parser("air", help="Dry-air ideal-gas properties")
    p.add_argument("--temp",          type=float, required=True)
    p.add_argument("--temp-unit",     type=str,   default="K",   dest="temp_unit")
    p.add_argument("--pressure",      type=float, default=101325)
    p.add_argument("--pressure-unit", type=str,   default="Pa",  dest="pressure_unit")

    # isentropic
    p = sub.add_parser("isentropic", help="Isentropic exit temperature")
    p.add_argument("--T1",     type=float, required=True)
    p.add_argument("--P1",     type=float, required=True)
    p.add_argument("--P2",     type=float, required=True)
    p.add_argument("--gamma",  type=float, default=1.4)
    p.add_argument("--T-unit", type=str,   default="K",   dest="T_unit")
    p.add_argument("--P-unit", type=str,   default="kPa", dest="P_unit")

    # polytropic
    p = sub.add_parser("polytropic", help="Polytropic exit temperature")
    p.add_argument("--T1",     type=float, required=True)
    p.add_argument("--P1",     type=float, required=True)
    p.add_argument("--P2",     type=float, required=True)
    p.add_argument("--n",      type=float, required=True)
    p.add_argument("--T-unit", type=str,   default="K",   dest="T_unit")
    p.add_argument("--P-unit", type=str,   default="kPa", dest="P_unit")

    # carnot
    p = sub.add_parser("carnot", help="Carnot efficiency and COP")
    p.add_argument("--T-hot",  type=float, required=True, dest="T_hot")
    p.add_argument("--T-cold", type=float, required=True, dest="T_cold")
    p.add_argument("--T-unit", type=str,   default="K",   dest="T_unit")

    # gibbs
    p = sub.add_parser("gibbs", help="Gibbs free energy g = h – Ts")
    p.add_argument("--enthalpy", type=float, required=True, help="h [kJ/kg]")
    p.add_argument("--temp",     type=float, required=True, help="T [K]")
    p.add_argument("--entropy",  type=float, required=True, help="s [kJ/(kg·K)]")

    # phase
    p = sub.add_parser("phase", help="Phase classification")
    p.add_argument("fluid",           type=str,   nargs="?", default="water")
    p.add_argument("--temp",          type=float, required=True)
    p.add_argument("--temp-unit",     type=str,   default="K",  dest="temp_unit")
    p.add_argument("--pressure",      type=float, required=True)
    p.add_argument("--pressure-unit", type=str,   default="Pa", dest="pressure_unit")

    # saturation
    p = sub.add_parser("saturation", help="Water saturation table")
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--temp",         type=float)
    grp.add_argument("--pressure",     type=float)
    p.add_argument("--temp-unit",      type=str, default="K",  dest="temp_unit")
    p.add_argument("--pressure-unit",  type=str, default="Pa", dest="pressure_unit")

    # fluids
    sub.add_parser("fluids",  help="List built-in fluids")

    # version
    sub.add_parser("version", help="Show version")

    return parser


_CMDS = {
    "convert":    cmd_convert,
    "steam":      cmd_steam,
    "air":        cmd_air,
    "isentropic": cmd_isentropic,
    "polytropic": cmd_polytropic,
    "carnot":     cmd_carnot,
    "gibbs":      cmd_gibbs,
    "phase":      cmd_phase,
    "saturation": cmd_saturation,
    "fluids":     cmd_fluids,
    "version":    cmd_version,
}


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    fn = _CMDS.get(args.command)
    if fn is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1
    try:
        return fn(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
