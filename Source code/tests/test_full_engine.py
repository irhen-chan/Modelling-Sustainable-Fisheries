
import numpy as np
import pytest
from src.utils import pressure_matrix, density_multiplier, catch_mix_str
from src.simulation import simulate
from src.fleet import FollowerFleet, TerritorialFleet, rng
from src.config import PARAMS

# ------------------------------------------------------------
def test_pressure_rowsum():
    P = PARAMS["baseline_migration"]
    h = np.arange(5)
    P_eff = pressure_matrix(P, h, alpha=0.6)
    assert np.allclose(P_eff.sum(axis=1), 1.0)

# ------------------------------------------------------------
@pytest.mark.parametrize("ratio, expected", [
    (0.35, 1.0),
    (0.25, 0.4),
    (0.05, 0.1),
])
def test_density_multiplier(ratio, expected):
    cap = 1.0
    mult = density_multiplier(biomass=ratio*cap,
                              cap=cap,
                              thresholds=PARAMS["density_thresholds"])
    assert np.isclose(mult, expected)

# ------------------------------------------------------------
def test_catch_mix_str():
    assert catch_mix_str(['C', 'C']) == 'C'
    assert catch_mix_str(['D'])      == 'D'
    assert catch_mix_str(['C', 'D']) == 'CD'

# ------------------------------------------------------------
def test_heuristic_move_logic():
    biomasses = np.array([0.8, 0.9, 0.95, 0.7, 0.6])
    follower   = FollowerFleet(idx=0, zone=0)
    territorial = TerritorialFleet(idx=1, zone=4)

    P = PARAMS["baseline_migration"]

    follower.move(P, biomasses)
    assert follower.zone == 2     # densest zone (index 2)

    # Territorial should stay put (local ratio 0.6 > 0.3)
    territorial.move(P, biomasses)
    assert territorial.zone == 4

    # Drop local biomass below threshold → should relocate
    biomasses[4] = 0.1
    territorial.move(P, biomasses)
    assert territorial.zone != 4

# ------------------------------------------------------------
def test_simulate_conservation():
    # 10-day tiny run, no metrics
    fleets = [FollowerFleet(idx=i, zone=i%5) for i in range(5)]
    zones, fleets = simulate(days=10,
                             alpha=0.6,
                             speed_factor=1.0,
                             fleet_list=fleets,
                             record_metrics=False)
    total_biomass = sum(z.biomass for z in zones)
    assert 0.0 < total_biomass <= sum(PARAMS["carrying_caps"])

# ------------------------------------------------------------
def test_simulate_decision_dynamics():
    # seed 20 % initial defectors → expect coop_rate < 1 after 30 days
    fleets = []
    for i in range(10):
        klass = FollowerFleet if i % 2 == 0 else TerritorialFleet
        strat = 'D' if rng.random() < 0.2 else 'C'
        fleets.append(klass(idx=i, strategy=strat, zone=rng.integers(5)))

    df = simulate(days=30,
                  alpha=0.6,
                  speed_factor=1.0,
                  fleet_list=fleets,
                  record_metrics=True)
    assert df["C"].iloc[-1] < 1.0
