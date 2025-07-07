# Modelling-Sustainable-Fisheries 🌊🎣  
*FIT3139 Final Project by Snehar Singh Gujral (2025)*

> An **agent-based model** coupling an **Iterated Prisoner’s Dilemma** fleet strategy with a **five-zone Markov-chain** tuna migration to explore over-fishing in Himalayan reservoirs.  
> The work evaluates skittish-fish behaviour, spatial chokepoints and territorial vs follower fleets across 100+ Monte-Carlo runs.

Growing up fishing in Himachal Pradesh, I wondered **which management levers actually keep stocks like the Golden Mahseer alive?**  
This project turns that question into code by:

* Modelling fish migration as a **discrete-time Markov chain** over five depth-linked zones.  
* Representing each fishing boat as an **agent** choosing *cooperate* (respect quotas) or *defect* (over-fish) in an **Iterated Prisoner’s Dilemma**.  
* Introducing a **skittishness parameter α** so fish flee crowded zones.  
* Running **Monte-Carlo simulations** to quantify biomass, profit, and conflict hot-spots.

Please find the in-depth analysis in the Report.

Academic-Integrity Notice
This repository contains work submitted for assessment in FIT3139 (2025) at Monash University.
It is published for portfolio and learning purposes only.
Current students must not submit any part of this code or report as their own.
