import unittest

from carbon_cost_pareto import analyze_scenarios, dominates, score_scenarios


class ParetoTests(unittest.TestCase):
    def test_frontier_keeps_tradeoffs_and_removes_dominated_case(self):
        rows = [
            {"scenario_id": "a", "annual_energy_kwh": "100", "price_yuan_per_kwh": "1", "emission_factor_kgco2e_per_kwh": "1", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "0"},
            {"scenario_id": "b", "annual_energy_kwh": "120", "price_yuan_per_kwh": "1", "emission_factor_kgco2e_per_kwh": "0.5", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "0"},
            {"scenario_id": "c", "annual_energy_kwh": "110", "price_yuan_per_kwh": "1", "emission_factor_kgco2e_per_kwh": "1", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "1"},
        ]
        report = analyze_scenarios(rows)
        self.assertEqual(set(report["frontier_scenario_ids"]), {"a", "b"})
        self.assertEqual(report["dominated_by"]["c"], ["a"])

    def test_identical_scenarios_do_not_dominate_each_other(self):
        rows = [
            {"scenario_id": "one", "annual_energy_kwh": "10", "price_yuan_per_kwh": "1", "emission_factor_kgco2e_per_kwh": "1", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "0"},
            {"scenario_id": "two", "annual_energy_kwh": "10", "price_yuan_per_kwh": "1", "emission_factor_kgco2e_per_kwh": "1", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "0"},
        ]
        scored = score_scenarios(rows)
        self.assertFalse(dominates(scored[0], scored[1]))
        self.assertEqual(set(analyze_scenarios(rows)["frontier_scenario_ids"]), {"one", "two"})

    def test_negative_comfort_penalty_is_rejected(self):
        row = {"scenario_id": "bad", "annual_energy_kwh": "10", "price_yuan_per_kwh": "1", "emission_factor_kgco2e_per_kwh": "1", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "-1"}
        with self.assertRaises(ValueError):
            score_scenarios([row])


if __name__ == "__main__":
    unittest.main()
