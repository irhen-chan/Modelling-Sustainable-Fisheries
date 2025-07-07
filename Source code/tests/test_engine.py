# tests/conftest.py
import sys, os
# insert the project root (one level up from tests/) into sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_no_mass_creation():
    """Biomass + cumulative catch should never exceed initial total."""
    from src.simulation import init_world, simulate_step
    zones, fleets = init_world()
    init_total = sum(z.biomass for z in zones)
    caught = 0.0
    for t in range(100):
        # track catch by diff in biomass + regen
        prev = sum(z.biomass for z in zones)
        simulate_step(zones, fleets, t)
        new  = sum(z.biomass for z in zones)
        caught += max(0, prev - new)
        assert sum(z.biomass for z in zones) + caught <= init_total * 1.05  # 5% slack


import numpy as np
from src.utils import pressure_matrix
from src.simulation import init_world, simulate_step
from src.config import PARAMS

def test_pressure_matrix_rowsum():
    P = PARAMS["baseline_migration"]
    h = np.arange(5)
    P_eff = pressure_matrix(P, h, PARAMS["alpha_default"])
    assert np.allclose(P_eff.sum(axis=1), 1.0)

def test_biomass_bounds():
    zones, fleets = init_world()
    for t in range(50):
        simulate_step(zones, fleets, t)
    for z in zones:
        assert 0.0 <= z.biomass <= z.carrying_cap
        