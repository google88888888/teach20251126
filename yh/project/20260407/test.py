from ortools.sat.python import cp_model
from typing import List, Dict, Any
import json
def group_deposits_optimal(deposits: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    使用整数规划精确求解分组问题。
    目标：1) 最大化满足条件的组数（金额≥12000且人数≤7）；
         2) 在满足1)的前提下，最小化使用的总组数（即尽可能合并，避免产生不满足的小组）。
    返回分组列表。
    """
    amounts = [int(d["存款金额数值(万)"]) for d in deposits]
    N = len(amounts)
    G = N  # 最大可能组数

    model = cp_model.CpModel()

    # x[i][g] = 1 表示物品 i 放入组 g
    x = [[model.NewBoolVar(f'x_{i}_{g}') for g in range(G)] for i in range(N)]

    # 每个物品恰好分到一个组
    for i in range(N):
        model.Add(sum(x[i][g] for g in range(G)) == 1)

    # 每组的金额和人数
    total = [model.NewIntVar(0, sum(amounts), f'total_{g}') for g in range(G)]
    count = [model.NewIntVar(0, 7, f'count_{g}') for g in range(G)]
    for g in range(G):
        model.Add(total[g] == sum(amounts[i] * x[i][g] for i in range(N)))
        model.Add(count[g] == sum(x[i][g] for i in range(N)))
        model.Add(count[g] <= 7)

    # 组是否非空
    nonempty = [model.NewBoolVar(f'nonempty_{g}') for g in range(G)]
    for g in range(G):
        # 非空 <=> 至少有一个物品
        model.Add(sum(x[i][g] for i in range(N)) >= 1).OnlyEnforceIf(nonempty[g])
        model.Add(sum(x[i][g] for i in range(N)) == 0).OnlyEnforceIf(nonempty[g].Not())

    # 组是否满足条件（金额≥12000且人数≤7，人数已约束）
    satisfied = [model.NewBoolVar(f'satisfied_{g}') for g in range(G)]
    for g in range(G):
        model.Add(total[g] >= 12000).OnlyEnforceIf(satisfied[g])
        # 注意：如果金额≥12000但 satisfied[g]=0，模型不会主动选，但目标会鼓励为1
        # 可选：添加反向约束（金额<12000 => satisfied[g]=0），但非必须

    # 目标：最大化满足条件的组数，同时最小化使用的总组数（即最小化非空组数）
    # 权重：满足组数权重远大于总组数权重（例如乘以 N+1）
    model.Maximize(
        (N + 1) * sum(satisfied) - sum(nonempty)
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"最优满足组数 = {solver.Value(sum(satisfied))}")
        groups = []
        for g in range(G):
            group_items = []
            for i in range(N):
                if solver.Value(x[i][g]) == 1:
                    group_items.append(deposits[i])
            if group_items:
                groups.append(group_items)
        return groups
    else:
        print("未找到可行解")
        return []


# 示例运行
if __name__ == "__main__":
    data = [
        {"客户名称": "九阳1", "存款金额": "1000万元", "存款金额数值(万)": 1000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳2", "存款金额": "2000万元", "存款金额数值(万)": 2000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳3", "存款金额": "3000万元", "存款金额数值(万)": 3000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳4", "存款金额": "4000万元", "存款金额数值(万)": 4000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳5", "存款金额": "5000万元", "存款金额数值(万)": 5000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳6", "存款金额": "6000万元", "存款金额数值(万)": 6000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳7", "存款金额": "7000万元", "存款金额数值(万)": 7000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳8", "存款金额": "7000万元", "存款金额数值(万)": 8000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳9", "存款金额": "7000万元", "存款金额数值(万)": 9000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳10", "存款金额": "7000万元", "存款金额数值(万)": 10000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳11", "存款金额": "7000万元", "存款金额数值(万)": 1000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳12", "存款金额": "7000万元", "存款金额数值(万)": 2000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
        {"客户名称": "九阳13", "存款金额": "7000万元", "存款金额数值(万)": 3000.0,
         "起息日": "2026年4月2日", "到期日": "2026年4月30日", "对客高收益报价": "1.9%"},
    ]

    test_result_data = group_deposits_optimal(data)
    with open('test_result_data.json', 'w', encoding='utf-8') as f:
        json.dump(test_result_data, f, ensure_ascii=False, indent=4)

    for i, group in enumerate(test_result_data, 1):
        total = sum(d["存款金额数值(万)"] for d in group)
        status = "满足" if total >= 12000 and len(group) <= 7 else "不满足"
        print(f"\n第{i}组（{len(group)}个，总和{total}万）{status}:")
        for d in group:
            print(f"  {d['客户名称']} {d['存款金额数值(万)']}")