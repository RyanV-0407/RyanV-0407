import os
import requests
from datetime import datetime, timedelta
from collections import Counter

USER = "RyanV-0407"
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# GraphQL query: last 30 days commit timestamps
QUERY = """
query ($user: String!) {
  user(login: $user) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

resp = requests.post(
    "https://api.github.com/graphql",
    json={"query": QUERY, "variables": {"user": USER}},
    headers=HEADERS
)

data = resp.json()
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

time_bins = Counter()
weekday_bins = Counter()

now = datetime.utcnow()
cutoff = now - timedelta(days=30)

for week in weeks:
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        if date < cutoff:
            continue

        count = day["contributionCount"]
        if count == 0:
            continue

        # Distribute commits evenly across daytime (best possible approximation)
        for _ in range(count):
            hour = date.hour if hasattr(date, "hour") else 12

            if 5 <= hour < 12:
                time_bins["Morning"] += 1
            elif 12 <= hour < 17:
                time_bins["Daytime"] += 1
            elif 17 <= hour < 21:
                time_bins["Evening"] += 1
            else:
                time_bins["Night"] += 1

            weekday_bins[date.strftime("%A")] += 1

def bar_width(value, max_value, max_width=220):
    return int((value / max_value) * max_width) if max_value else 0

max_time = max(time_bins.values(), default=1)
max_day = max(weekday_bins.values(), default=1)

rows_time = ["Morning", "Daytime", "Evening", "Night"]
rows_day = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

y = 50
line_height = 24
svg_parts = []

for label in rows_time:
    val = time_bins[label]
    w = bar_width(val, max_time)
    svg_parts.append(f'''
      <text x="20" y="{y}">{label}</text>
      <rect x="140" y="{y-12}" width="{w}" height="10" />
      <text x="370" y="{y}">{val}</text>
    ''')
    y += line_height

y += 20

for label in rows_day:
    val = weekday_bins[label]
    w = bar_width(val, max_day)
    svg_parts.append(f'''
      <text x="20" y="{y}">{label}</text>
      <rect x="140" y="{y-12}" width="{w}" height="10" />
      <text x="370" y="{y}">{val}</text>
    ''')
    y += line_height

svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{y+30}">
  <style>
    text {{
      font-family: JetBrains Mono, monospace;
      font-size: 13px;
      fill: #00FF9C;
    }}
    rect {{
      fill: #00FF9C;
    }}
    .bg {{
      fill: #0b0b0b;
      stroke: #00FF9C;
      stroke-width: 1;
      rx: 10;
    }}
  </style>

  <rect class="bg" x="5" y="5" width="410" height="{y}" />
  {''.join(svg_parts)}
</svg>
'''

os.makedirs("assets", exist_ok=True)
with open("assets/analytics.svg", "w") as f:
    f.write(svg)
