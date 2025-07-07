from dataclasses import dataclass, field

@dataclass
class Zone:
    """
    A single spatial cell that stores fish biomass and
    keeps track of which fleet indices are currently on it.
    """
    name: str
    biomass: float
    carrying_cap: float
    fleets_here: list[int] = field(default_factory=list)

    # ── biology ────────────────────────────────────────────
    def harvest(self,
                mix: str,
                density_mult: float,
                catch_rates: dict[str, float]) -> float:
        """
        Remove biomass according to fleet strategy mix and density control.
        mix ∈ {'C','D','CC','CD','DD'}  → boils down to 'C' or 'D'.
        density_mult ≤ 1 reduces catch when stocks are low.
        """
        base_key  = mix if mix in ("C", "D") else mix[-1]      # 'CC'→C, 'CD'→D…
        rate      = catch_rates[base_key] * density_mult
        catch_amt = min(self.biomass, rate * self.biomass)

        self.biomass -= catch_amt
        return catch_amt

    def regen(self, r: float = 0.05):
        """Simple logistic regrowth towards carrying capacity."""
        self.biomass += r * self.biomass * (1 - self.biomass / self.carrying_cap)
