# Carbon Cost Pareto

比较一组虚构的年度用能情景，计算每个情景的年费用和排放估值，再找出成本、碳排放与舒适度惩罚之间的 Pareto 前沿。结果用于展示多目标权衡，不会自动选择或控制方案。

## 运行

需要 Python 3.9 或更高版本，不需要第三方包。

```bash
python carbon_cost_pareto.py
python -m unittest discover -s tests -v
```

首次运行生成可编辑的 `data/scenarios.csv`；之后读取已有文件。列为 `scenario_id,description,annual_energy_kwh,price_yuan_per_kwh,emission_factor_kgco2e_per_kwh,annualized_extra_cost_yuan,comfort_penalty_points`。结果写入 `results/report.json` 和 `results/scored_scenarios.csv`。

## 术语

- **年化额外成本**：为比较而折算到一年的额外成本假设。
- **舒适度惩罚点数**：示例定义的相对指标，数值越低表示惩罚越小；它不是温度、满意度或合规标准。
- **Pareto 支配**：若某情景在所有目标上都不差于另一个，且至少一个目标更好，则称其支配另一个。
- **Pareto 前沿**：当前假设下未被其他情景支配的集合；集合内通常存在目标间权衡。

## 数据和边界

示例情景完全虚构。电价和排放因子是可编辑占位输入，低碳电力情景中的排放因子不代表任何真实供应合同。舒适度惩罚只是教学变量。模型没有验证工程可行性、法规、科研流程、投资风险或真实舒适度。前沿只表达输入数值间的数学权衡，不是节能承诺、投资结论或运行指令；任何实际方案都需由设施、财务和使用者共同核实。
