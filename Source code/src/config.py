import numpy as np

PARAMS: dict = {

    # ――― 1.  Spatial layout ―――
    "zones": ["Z0", "Z1", "Z2", "Z3", "Z4"],

    # Tonnes of biomass at pristine equilibrium (same order as zones list)
    "carrying_caps": np.array([1.0, 1.0, 1.0, 1.0, 1.0]),


    # ――― 2.  Baseline migration (Markov chain) ―――
    # rows = current zone, cols = prob. a fish moves to that next zone
    "baseline_migration": np.array([
        [0.60, 0.15, 0.10, 0.10, 0.05],
        [0.10, 0.60, 0.15, 0.10, 0.05],
        [0.05, 0.10, 0.60, 0.15, 0.10],
        [0.10, 0.05, 0.10, 0.60, 0.15],
        [0.15, 0.10, 0.05, 0.10, 0.60],
    ]),
    #number of fleets

    "n_fleets": 50,

    # ――― 3.  Default α (alpha) for density-dependent catch curve ―――
    # Think of α as the steepness of how catch efficiency drops with scarcity
    "alpha_default": 0.6,           # 0 ≈ flat, 1 ≈ linear, >1 ≈ steep


    # ――― 4.  Density thresholds (biomass ÷ cap) ―――
    # Used to switch heuristics or trigger catch-rate scaling
    "density_thresholds": {
        "warning": 0.40,            # below 40 % of cap  → low-density regime
        "critical": 0.10,           # below 10 %         → emergency
    },


    # ――― 5.  Catch-rates table (fraction of zone biomass taken per boat) ―――
    # Key = fleet action in the Iterated Prisoner’s Dilemma
    "catch_rates": {
        "C": 0.05,                  # sustainable / cooperate
        "D": 0.15,                  # aggressive  / defect
    },


    "migration_winter": np.array([
    [0.55, 0.20, 0.10, 0.10, 0.05],
    [0.20, 0.55, 0.10, 0.10, 0.05],
    [0.10, 0.15, 0.55, 0.15, 0.05],
    [0.10, 0.10, 0.15, 0.55, 0.10],
    [0.05, 0.10, 0.10, 0.20, 0.55],
])

} 