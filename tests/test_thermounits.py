"""
tests/test_thermounits.py
=========================
Comprehensive test suite for thermounits.

Run with:  pytest tests/ -v
"""

import math
import pytest

from thermounits.units import ureg, Dimension
from thermounits.units.quantity import Quantity, DimensionError
from thermounits.units.dimensions import (
    TEMPERATURE, PRESSURE, SPECIFIC_ENERGY, SPECIFIC_ENTROPY,
    ENERGY, DENSITY,
)
from thermounits.thermo.phase import (
    PhaseState, sat_pressure_water, sat_temperature_water,
    phase_of_water, phase_of_air,
)
from thermounits.thermo.functions import (
    enthalpy_ideal_gas, entropy_ideal_gas,
    gibbs_free_energy, helmholtz_free_energy,
    internal_energy,
    isentropic_temperature, isentropic_pressure,
    carnot_efficiency, cop_refrigerator, cop_heat_pump,
    heat_of_vaporisation, energy_balance,
)
from thermounits.fluids.water import WaterProperties
from thermounits.fluids.air import AirProperties, R_AIR


class TestQuantity:

    def test_construction_and_repr(self):
        q = ureg.quantity(300, "K")
        assert q.value == pytest.approx(300.0)
        assert "300" in repr(q)

    def test_immutability(self):
        q = ureg.quantity(300, "K")
        with pytest.raises(AttributeError):
            q._value = 400

    def test_addition_same_dim(self):
        a = ureg.quantity(100, "K")
        b = ureg.quantity(200, "K")
        c = a + b
        assert c.value == pytest.approx(300.0)

    def test_addition_different_dim_raises(self):
        T = ureg.quantity(300, "K")
        P = ureg.quantity(101325, "Pa")
        with pytest.raises(DimensionError):
            _ = T + P

    def test_multiplication_by_scalar(self):
        q = ureg.quantity(5, "kJ/kg")
        r = q * 2
        assert r.value == pytest.approx(10_000.0)

    def test_comparison(self):
        a = ureg.quantity(200, "K")
        b = ureg.quantity(300, "K")
        assert a < b
        assert b > a
        assert a == ureg.quantity(200, "K")


class TestUnitConversions:

    def test_celsius_to_kelvin(self):
        T_c = ureg.quantity(0, "°C")
        assert T_c.to("K").value == pytest.approx(273.15, rel=1e-6)

    def test_fahrenheit_to_kelvin(self):
        T_f = ureg.quantity(32, "°F")
        assert T_f.to("K").value == pytest.approx(273.15, rel=1e-4)

    def test_kelvin_to_celsius(self):
        T = ureg.quantity(373.15, "K")
        assert T.to("°C").value == pytest.approx(100.0, rel=1e-5)

    def test_atm_to_pa(self):
        P = ureg.quantity(1, "atm")
        assert P.to("Pa").value == pytest.approx(101325.0, rel=1e-6)

    def test_btu_to_joule(self):
        E = ureg.quantity(1, "BTU")
        assert E.to("J").value == pytest.approx(1055.06, rel=1e-4)

    def test_dimension_mismatch_raises(self):
        T = ureg.quantity(300, "K")
        with pytest.raises(DimensionError):
            T.to("Pa")


class TestWaterPhase:

    def test_subcooled_liquid(self):
        assert phase_of_water(323.15, 500_000) == PhaseState.SUBCOOLED_LIQUID

    def test_superheated_vapour(self):
        assert phase_of_water(473.15, 101325) == PhaseState.SUPERHEATED_VAPOUR

    def test_supercritical(self):
        assert phase_of_water(650.0, 23e6) == PhaseState.SUPERCRITICAL

    def test_below_triple_raises(self):
        with pytest.raises(ValueError):
            phase_of_water(270.0, 101325)

    def test_sat_pressure_at_100C(self):
        assert sat_pressure_water(373.15) == pytest.approx(101_325, rel=0.02)

    def test_sat_temperature_round_trip(self):
        T_in = 400.0
        P_sat = sat_pressure_water(T_in)
        T_out = sat_temperature_water(P_sat)
        assert T_out == pytest.approx(T_in, rel=1e-4)


class TestThermodynamicFunctions:

    def test_enthalpy_at_ref_zero(self):
        T  = ureg.quantity(298.15, "K")
        cp = ureg.quantity(1005.0, "J/(kg·K)")
        h  = enthalpy_ideal_gas(T, cp)
        assert h.value == pytest.approx(0.0, abs=1.0)

    def test_isentropic_T_known_value(self):
        T1 = ureg.quantity(300.0, "K")
        P1 = ureg.quantity(100.0, "kPa")
        P2 = ureg.quantity(500.0, "kPa")
        T2 = isentropic_temperature(T1, P1, P2, 1.4)
        expected = 300.0 * (5.0) ** (0.4 / 1.4)
        assert T2.value == pytest.approx(expected, rel=1e-6)

    def test_carnot_efficiency(self):
        Th = ureg.quantity(800.0, "K")
        Tc = ureg.quantity(300.0, "K")
        assert carnot_efficiency(Th, Tc) == pytest.approx(0.625, rel=1e-6)

    def test_cop_hp_equals_cop_r_plus_one(self):
        Th = ureg.quantity(350.0, "K")
        Tc = ureg.quantity(270.0, "K")
        assert cop_heat_pump(Th, Tc) == pytest.approx(cop_refrigerator(Th, Tc) + 1.0, rel=1e-6)

    def test_gibbs_definition(self):
        h = ureg.quantity(2000.0, "kJ/kg")
        T = ureg.quantity(400.0,  "K")
        s = ureg.quantity(5.0,    "kJ/(kg·K)")
        g = gibbs_free_energy(h, T, s)
        expected = h.value - T.value * s.value
        assert g.value == pytest.approx(expected, rel=1e-6)

    def test_energy_balance_zero_residual(self):
        q   = ureg.quantity(500_000, "J/kg")
        w   = ureg.quantity(200_000, "J/kg")
        dh  = ureg.quantity(300_000, "J/kg")
        res = energy_balance(q, w, dh)
        assert res.value == pytest.approx(0.0, abs=1e-6)


class TestWaterProperties:

    def setup_method(self):
        self.wp = WaterProperties()

    def test_superheated_steam(self):
        state = self.wp.at_T_P(ureg.quantity(200, "°C"), ureg.quantity(101325, "Pa"))
        assert state.phase == PhaseState.SUPERHEATED_VAPOUR
        assert state.enthalpy.value > 2_000_000

    def test_saturation_pressure_at_100C(self):
        props = self.wp.saturation_at_T(ureg.quantity(373.15, "K"))
        assert props["pressure"].value == pytest.approx(101_325, rel=0.02)

    def test_latent_heat_at_100C(self):
        props = self.wp.saturation_at_T(ureg.quantity(373.15, "K"))
        assert props["h_vap"].value == pytest.approx(2_256_000, rel=0.05)


class TestAirProperties:

    def setup_method(self):
        self.ap = AirProperties()

    def test_density_ideal_gas(self):
        T   = ureg.quantity(300, "K")
        P   = ureg.quantity(101325, "Pa")
        rho = self.ap.density(T, P)
        assert rho.value == pytest.approx(101325 / (R_AIR * 300), rel=1e-4)

    def test_gamma_near_1_4(self):
        assert 1.35 < self.ap.gamma(ureg.quantity(300, "K")) < 1.42

    def test_speed_of_sound(self):
        c = self.ap.speed_of_sound(ureg.quantity(293.15, "K"))
        assert 335 < c.value < 350


class TestFluidRegistry:

    def test_lookup_and_alias(self):
        from thermounits.fluids.fluid import fluids
        assert fluids.get("steam").name == "water"

    def test_unknown_raises(self):
        from thermounits.fluids.fluid import fluids
        with pytest.raises(KeyError):
            fluids.get("unobtainium")

    def test_gamma_relation(self):
        from thermounits.fluids.fluid import fluids
        f = fluids.get("air")
        assert f.gamma == pytest.approx(f.cp_gas / f.cv_gas, rel=1e-6)


class TestCLI:

    def _run(self, args):
        from thermounits.cli.main import main
        return main(args)

    def test_version(self):
        assert self._run(["version"]) == 0

    def test_convert(self, capsys):
        assert self._run(["convert", "100", "degC", "K"]) == 0
        assert "373" in capsys.readouterr().out

    def test_carnot(self, capsys):
        assert self._run(["carnot", "--T-hot", "800", "--T-cold", "300"]) == 0
        assert "0.625" in capsys.readouterr().out

    def test_steam(self, capsys):
        assert self._run(["steam", "--temp", "200", "--temp-unit", "degC", "--pressure", "101325"]) == 0
        assert "superheated" in capsys.readouterr().out.lower()

    def test_air(self, capsys):
        assert self._run(["air", "--temp", "25", "--temp-unit", "degC"]) == 0

    def test_isentropic(self, capsys):
        assert self._run(["isentropic", "--T1", "300", "--P1", "100", "--P2", "500", "--gamma", "1.4"]) == 0
        assert "475" in capsys.readouterr().out

    def test_saturation(self, capsys):
        assert self._run(["saturation", "--temp", "373.15"]) == 0
        assert "latent" in capsys.readouterr().out.lower() or "h_fg" in capsys.readouterr().out

    def test_fluids_list(self, capsys):
        assert self._run(["fluids"]) == 0
        assert "water" in capsys.readouterr().out

    def test_gibbs(self):
        assert self._run(["gibbs", "--enthalpy", "2500", "--temp", "400", "--entropy", "6.7"]) == 0

    def test_bad_unit(self):
        assert self._run(["convert", "100", "badunit", "K"]) == 1
