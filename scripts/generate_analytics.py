import requests
from collections import Counter
from datetime import datetime
import os

USER = "RyanV-0407"
TOKEN = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"token {TOKEN}"
}

events = requests.get(
    f"https://api.github.com/users/{USER}/events/public",
    headers=headers
).json()

time_buckets = Counter()
weekday_buckets = Counter()

for e in events:
    if e.get("type") == "PushEvent":
        t = datetime.strptime(e["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        hour = t.hour

        if 5 <= hour < 12:
            time_buckets["Morning"] += 1
        elif 12 <= hour < 17:
            time_buckets["Daytime"] += 1
        elif 17 <= hour < 21:
            time_buckets["Evening"] += 1
        else:
            time_buckets["Night"] += 1

        weekday_buckets[t.strftime("%A")] += 1

def bar(value, max_value, width=18):
    filled = int((value / max_value) * width) if max_value else 0
    return "█" * filled + "░" * (width - filled)

max_time = max(time_buckets.values(), default=1)
max_day = max(weekday_buckets.values(), default=1)

lines = []

lines.append("Commit activity by time of day")
for k in ["Morning", "Daytime", "Evening", "Night"]:
    v = time_buckets[k]
    lines.append(f"{k:<10} {v:>3}  {bar(v, max_time)}")

lines.append("")
lines.append("Commits by weekday")
for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
    v = weekday_buckets[d]
    lines.append(f"{d:<10} {v:>3}  {bar(v, max_day)}")

text = "\n".join(lines)

svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="700" height="360">
  <style>
    text {{
      font-family: monospace;
      font-size: 14px;
      fill: #00FF9C;
      white-space: pre;
    }}
    rect {{
      fill: #0b0b0b;
      stroke: #00FF9C;
      stroke-width: 1;
    }}
  </style>
  <rect x="5" y="5" width="690" height="350" rx="8"/>
  <text x="20" y="30">{text}</text>
</svg>
"""

os.makedirs("assets", exist_ok=True)
with open("assets/analytics.svg", "w") as f:
    f.write(svg)
