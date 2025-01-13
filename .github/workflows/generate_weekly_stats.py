import json
import sys
from collections import defaultdict

def parse_pr_title(title: str):
    """Extract week and count from PR title."""
    try:
        parts = title.split()
        week, count = parts[0][1:2], parts[1][0:1]
        return int(week[0]), int(count[0])
    except (IndexError, ValueError):
        return None, None

def find_ordered_label(labels: dict):
    """Extract ordered label from label_data.json, order is followed by description"""
    return list(map(lambda x: x.get("name", ""),
                       sorted([label for label in labels],
                              key = lambda x: x.get("description", 0),
                              reverse=True)))

def find_best_label(ordered_labels: list, cur_labels: list):
    """Find the best label in PR"""
    for label in ordered_labels:
        if label in cur_labels:
            return label
    return None

def set_stats(prs:dict, targets:dict, all_labels:dict):
    """Set stats by PRs"""
    ordered_labels = find_ordered_label(all_labels)
    stats = defaultdict(lambda: {"solved": defaultdict(lambda: dict(zip(ordered_labels, [0 for _ in range(len(ordered_labels))]))), "target": 0})

    for pr in prs:
        title = pr.get("title", "")
        assignee = pr.get("assignee", {})
        assignee_login = assignee.get("login", "") if assignee else ""
        labels = [label["name"] for label in pr.get("labels", [])]
        label = find_best_label(ordered_labels, labels)

        week, _ = parse_pr_title(title)
        if week is None or assignee_login == "" or label is None:
            continue

        stats[assignee_login]["solved"][week][label] += 1

        stats[assignee_login]["target"] = targets.get(assignee_login, 0)
    return stats

def calculate_stats(data: dict, least_week: int, last_week: int, seminar: int):
    """Calculate weekly stats and total missed count"""
    total = 0
    target = data["target"]
    for week in range(least_week, last_week+1):
        solved = sum(data["solved"][week].values())
        total += max(0, target - solved)
    total -= seminar * target
    last_solved = sum(data["solved"][last_week].values())

    return last_solved, target, total

def generate_report(stats: dict):
    """Generate report"""
    week = max(max(data["solved"].keys()) for data in stats.values())
    report = f"### {week}주차 정산\n\n"
    seminar_list = []
    for idx, value in enumerate(stats.items()):
        user, data = value
        last_solved, target, total = calculate_stats(data, min(stats[user]["solved"].keys()), week, 0) # Need to update with seminar, each seminar total value decreased by target value
        if total >= target:
            seminar_list.append(user)
        report += f"{idx+1}. {user}\n"
        diff = max(0, target - last_solved)
        report += f"    - 금주 푼 문제 수: {last_solved}/{target} -> 부족: {diff} 누적: {total}\n"
        label_counts = ", ".join([f"{label}: {count}" for label, count in data["solved"][week].items()])
        report += f"    - 난이도 분포: {label_counts}\n\n"
    report += "### 세미나 대상자\n\n"
    report += ", ".join([f"{name}" for name in seminar_list])
    return report

def main(pr_file, target_goals, label_file, output_file):
    with open(pr_file, "r") as f_pr:
        prs = json.load(f_pr)

    with open(target_goals, "r") as f_tg:
        targets = json.load(f_tg)

    with open(label_file, "r") as f_label:
        all_labels = json.load(f_label)

    stats = set_stats(prs, targets, all_labels)
    report = generate_report(stats)

    with open(output_file, "w") as f:
        f.write(report)

if __name__ == "__main__":
    pr_file = sys.argv[1]
    target_goals = sys.argv[2]
    label_file = sys.argv[3]
    output_file = sys.argv[4]
    main(pr_file, target_goals, label_file, output_file)