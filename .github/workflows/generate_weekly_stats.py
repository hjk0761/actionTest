import json
import sys
from collections import defaultdict

def parse_pr_title(title):
    """Extract week and count from PR title."""
    try:
        parts = title.split()
        week, count = parts[0][1:-1], parts[1][:-1]
        return int(week[:-1]), int(count[:-1])
    except (IndexError, ValueError):
        return None, None

def load_target_goals():
    """Load target goals for each user."""
    # Example data: {username: target_count_per_week}
    return {"hjk0761": 5, "user2": 3}

def main(pr_file, output_file):
    with open(pr_file, "r") as f:
        prs = json.load(f)

    goals = load_target_goals()
    stats = defaultdict(lambda: {"solved": 0, "target": 0})

    for pr in prs:
        title = pr.get("title", "")
        assignee = pr.get("assignee", {})
        assignee_login = assignee.get("login", "") if assignee else "미지정"
        labels = [label["name"] for label in pr.get("labels", [])]

        week, _ = parse_pr_title(title)
        if week is None or assignee_login == "":
            continue

        # Increment solved count
        stats[assignee_login]["solved"] += 1

        # Update target count
        stats[assignee_login]["target"] = goals.get(assignee_login, 0)

    # Generate report
    report = "n주차 정산\n"
    for user, data in stats.items():
        solved, target = data["solved"], data["target"]
        diff = solved - target
        report += f"{user} - {solved}/{target} -> {diff}\n"

    with open(output_file, "w") as f:
        f.write(report)

if __name__ == "__main__":
    pr_file = sys.argv[1]
    output_file = sys.argv[2]
    main(pr_file, output_file)

