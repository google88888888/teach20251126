from ortools.sat.python import cp_model
from typing import List, Dict, Any
import json

def group_deposits_optimal(deposits: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    使用整数规划求解分组问题。
    目标优先级：
        1. 最大化满足条件的组数（金额≥12000且人数≤7）
        2. 在1的前提下，最大化满足组中的总项目数（即让不满足组尽量小）
        3. 在2的前提下，最小化使用的总组数
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
        model.Add(sum(x[i][g] for i in range(N)) >= 1).OnlyEnforceIf(nonempty[g])
        model.Add(sum(x[i][g] for i in range(N)) == 0).OnlyEnforceIf(nonempty[g].Not())

    # 组是否满足条件（金额≥12000）
    satisfied = [model.NewBoolVar(f'satisfied_{g}') for g in range(G)]
    for g in range(G):
        model.Add(total[g] >= 12000).OnlyEnforceIf(satisfied[g])
        model.Add(total[g] < 12000).OnlyEnforceIf(satisfied[g].Not())  # 加强逻辑

    # 满足组中的项目数：如果 satisfied[g]=1，则等于 count[g]；否则为0
    items_in_satisfied = [model.NewIntVar(0, 7, f'items_in_satisfied_{g}') for g in range(G)]
    for g in range(G):
        model.Add(items_in_satisfied[g] == count[g]).OnlyEnforceIf(satisfied[g])
        model.Add(items_in_satisfied[g] == 0).OnlyEnforceIf(satisfied[g].Not())

    # 目标：三层权重
    # 权重1: (N+1)^2 * sum(satisfied)    —— 最高优先级
    # 权重2: (N+1) * sum(items_in_satisfied) —— 次优先级
    # 权重3: - sum(nonempty)               —— 最低优先级（最小化总组数）
    model.Maximize(
        (N + 1) * (N + 1) * sum(satisfied)
        + (N + 1) * sum(items_in_satisfied)
        - sum(nonempty)
    )

    solver = cp_model.CpSolver()
    # 可以设置求解时间限制，例如 solver.parameters.max_time_in_seconds = 10.0
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

    result = group_deposits_optimal(data)
    with open('test_result_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    for i, group in enumerate(result, 1):
        total = sum(d["存款金额数值(万)"] for d in group)
        status = "满足" if total >= 12000 and len(group) <= 7 else "不满足"
        print(f"\n第{i}组（{len(group)}个，总和{total}万）{status}:")
        for d in group:
            print(f"  {d['客户名称']} {d['存款金额数值(万)']}万")