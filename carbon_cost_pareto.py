"""Compare fictional annual energy scenarios across cost, carbon, and comfort."""

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
INPUT_PATH = DATA_DIR / "scenarios.csv"
OBJECTIVES = ("annual_cost_yuan", "annual_emissions_kgco2e", "comfort_penalty_points")


def write_example(path=INPUT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"scenario_id": "baseline", "description": "参考情景", "annual_energy_kwh": "12000", "price_yuan_per_kwh": "0.72", "emission_factor_kgco2e_per_kwh": "0.536", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "0"},
        {"scenario_id": "efficient", "description": "节能设备假设", "annual_energy_kwh": "10000", "price_yuan_per_kwh": "0.72", "emission_factor_kgco2e_per_kwh": "0.536", "annualized_extra_cost_yuan": "500", "comfort_penalty_points": "1"},
        {"scenario_id": "cleaner-grid", "description": "低碳电力假设", "annual_energy_kwh": "11800", "price_yuan_per_kwh": "0.75", "emission_factor_kgco2e_per_kwh": "0.280", "annualized_extra_cost_yuan": "800", "comfort_penalty_points": "0"},
        {"scenario_id": "mixed", "description": "组合假设", "annual_energy_kwh": "10500", "price_yuan_per_kwh": "0.74", "emission_factor_kgco2e_per_kwh": "0.350", "annualized_extra_cost_yuan": "300", "comfort_penalty_points": "2"},
        {"scenario_id": "comfort-first", "description": "舒适优先对照", "annual_energy_kwh": "12500", "price_yuan_per_kwh": "0.72", "emission_factor_kgco2e_per_kwh": "0.536", "annualized_extra_cost_yuan": "0", "comfort_penalty_points": "0"},
        {"scenario_id": "balanced", "description": "均衡假设", "annual_energy_kwh": "10800", "price_yuan_per_kwh": "0.72", "emission_factor_kgco2e_per_kwh": "0.400", "annualized_extra_cost_yuan": "100", "comfort_penalty_points": "0"},
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_scenarios(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def score_scenarios(rows):
    seen = set()
    scored = []
    for line_number, row in enumerate(rows, start=2):
        scenario_id = (row.get("scenario_id") or "").strip()
        if not scenario_id:
            raise ValueError(f"line {line_number}: scenario_id is required")
        if scenario_id in seen:
            raise ValueError(f"line {line_number}: duplicate scenario_id {scenario_id}")
        seen.add(scenario_id)
        try:
            energy = float(row["annual_energy_kwh"])
            price = float(row["price_yuan_per_kwh"])
            factor = float(row["emission_factor_kgco2e_per_kwh"])
            extra_cost = float(row["annualized_extra_cost_yuan"])
            comfort = float(row["comfort_penalty_points"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"line {line_number}: scenario metrics must be numeric") from error
        if min(energy, price, factor, extra_cost, comfort) < 0:
            raise ValueError(f"line {line_number}: inputs must be non-negative")
        scored.append({
            "scenario_id": scenario_id,
            "description": (row.get("description") or "").strip(),
            "annual_energy_kwh": round(energy, 2),
            "annual_cost_yuan": round(energy * price + extra_cost, 2),
            "annual_emissions_kgco2e": round(energy * factor, 2),
            "comfort_penalty_points": round(comfort, 2),
        })
    return scored


def dominates(left, right):
    """Return true when left is no worse in every objective and better in at least one."""
    no_worse = all(left[key] <= right[key] for key in OBJECTIVES)
    strictly_better = any(left[key] < right[key] for key in OBJECTIVES)
    return no_worse and strictly_better


def pareto_frontier(scenarios):
    return [scenario for scenario in scenarios
            if not any(other is not scenario and dominates(other, scenario) for other in scenarios)]


def analyze_scenarios(rows):
    scored = score_scenarios(rows)
    frontier = pareto_frontier(scored)
    dominated_by = {}
    for scenario in scored:
        dominated_by[scenario["scenario_id"]] = [
            other["scenario_id"] for other in scored
            if other is not scenario and dominates(other, scenario)
        ]
    report = {
        "scenario_count": len(scored),
        "objectives_minimized": list(OBJECTIVES),
        "frontier_scenario_ids": [item["scenario_id"] for item in frontier],
        "dominated_by": dominated_by,
        "frontier": frontier,
        "all_scenarios": scored,
        "assumptions": {
            "emission_factors": "scenario inputs are illustrative placeholders and require source/year documentation",
            "comfort_penalty": "fictional relative points; lower is treated as better for comparison",
            "cost": "annual_energy_kwh * price_yuan_per_kwh + annualized_extra_cost_yuan",
        },
        "limitations": "Frontier shows trade-offs in supplied assumptions; it does not choose or control an option.",
    }
    return report


def run(input_path=INPUT_PATH):
    if not input_path.exists():
        write_example(input_path)
    report = analyze_scenarios(read_scenarios(input_path))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = list(report["all_scenarios"][0]) if report["all_scenarios"] else ["scenario_id"]
    with (RESULTS_DIR / "scored_scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report["all_scenarios"])
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    args = parser.parse_args()
    run(args.input)


if __name__ == "__main__":
    main()
