import feedparser
from datetime import datetime
from html import unescape
import re

# -----------------------------
# SUBJECTS & KEYWORDS
# -----------------------------

SUBJECT_ORDER = [
    "Economy",
    "Economic Issues and Reforms",
    "Agriculture",
    "Geopolitics",
    "National Security",
    "Foreign Policy",
    "Constitutional Law and Judiciary",
    "Gender",
    "Social Issues",
]

SUBJECT_KEYWORDS = {
    "Economy": [
        "economy", "economic growth", "gdp", "inflation", "interest rate",
        "sbp", "state bank", "pkru", "stock market", "psx",
        "fiscal deficit", "current account", "trade deficit", "remittances"
    ],
    "Economic Issues and Reforms": [
        "imf", "reforms", "privatisation", "privatization", "tax reform",
        "fbr", "revenue", "subsidy", "circular debt", "energy tariff",
        "structural reform", "privatising", "austerity"
    ],
    "Agriculture": [
        "agriculture", "crop", "wheat", "cotton", "rice", "sugarcane",
        "fertiliser", "fertilizer", "farmer", "livestock", "waterlogging",
        "canal", "irrigation", "agri"
    ],
    "Geopolitics": [
        "geopolitics", "great power", "china", "india", "us", "russia",
        "middle east", "gulf", "saudi", "iran", "turkey", "taliban",
        "multipolar", "cold war", "bloc"
    ],
    "National Security": [
        "terror", "terrorism", "militant", "ctd", "security forces",
        "army", "military", "nacta", "internal security", "insurgency",
        "balochistan unrest", "taksim", "counterterrorism"
    ],
    "Foreign Policy": [
        "foreign policy", "diplomacy", "bilateral", "summit",
        "oic", "unsc", "united nations", "strategic partnership",
        "border", "kashmir", "fm", "foreign office", "fo spokesperson"
    ],
    "Constitutional Law and Judiciary": [
        "supreme court", "sc", "high court", "lhr hc", "shc", "ihc",
        "constitution", "constitutional", "article", "basic structure",
        "judiciary", "bench", "locus standi", "habeas corpus", "reference"
    ],
    "Gender": [
        "women", "gender", "harassment", "violence against women",
        "domestic violence", "honour killing", "honor killing",
        "girls’ education", "women’s rights", "gender parity",
        "sexual harassment"
    ],
    "Social Issues": [
        "poverty", "inequality", "healthcare", "education", "literacy",
        "housing", "slums", "informal settlements", "malnutrition",
        "stunting", "public health", "epidemic", "social safety net",
        "bisp", "ehsaas", "youth", "labour", "labor rights"
    ],
}

# -----------------------------
# RSS FEEDS (Dawn + Tribune)
# -----------------------------

FEEDS = {
    "Dawn": [
        # Main news feed (includes politics, business, etc.)
        "https://www.dawn.com/feeds/home"
    ],
    "The Express Tribune": [
        # From Tribune's RSS hub: latest + opinion/editorial feeds
        "https://tribune.com.pk/feed/latest",
        "https://tribune.com.pk/feed/opinion",
    ],
}

# -----------------------------
# HELPERS
# -----------------------------

def strip_html(text: str) -> str:
    """Remove HTML tags & unescape entities."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def classify_subject(title: str, summary: str) -> str | None:
    """Rudimentary classifier: match by keyword in title + summary."""
    blob = (title + " " + summary).lower()
    for subject in SUBJECT_ORDER:
        for kw in SUBJECT_KEYWORDS[subject]:
            if kw.lower() in blob:
                return subject
    return None


def fetch_articles():
    """Fetch and classify articles from all feeds."""
    classified = {subject: [] for subject in SUBJECT_ORDER}

    for source, urls in FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                print(f"[WARN] Could not parse feed {url}: {e}")
                continue

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                summary = strip_html(entry.get("summary", ""))
                link = entry.get("link", "").strip()

                subject = classify_subject(title, summary)
                if not subject:
                    continue

                item = {
                    "source": source,
                    "title": title,
                    "summary": summary,
                    "link": link,
                }
                classified[subject].append(item)

    # Optional: truncate each subject to top N items
    MAX_PER_SUBJECT = 6
    for subject in SUBJECT_ORDER:
        classified[subject] = classified[subject][:MAX_PER_SUBJECT]

    return classified


def build_html(classified: dict) -> str:
    """Build the newsletter.html content."""
    date_str = datetime.now().strftime("%d %B %Y")

    parts: list[str] = []

    # HTML + basic CSS (no templating engine needed)
    parts.append(
"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>CSS Current Affairs Newsletter</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --primary: #035076;
      --bg: #f5f7fb;
      --card-bg: #ffffff;
      --text-main: #111827;
      --text-muted: #6b7280;
      --border: #e5e7eb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 0;
      font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg);
      color: var(--text-main);
    }
    .container {
      max-width: 900px;
      margin: 24px auto 40px;
      padding: 0 16px;
    }
    header {
      background: var(--primary);
      color: white;
      padding: 20px 16px;
      margin: -8px 0 24px;
    }
    header h1 {
      margin: 0;
      font-size: 1.8rem;
      font-weight: 600;
    }
    header p {
      margin: 4px 0 0;
      font-size: 0.95rem;
      opacity: 0.85;
    }
    .date {
      margin: 0 0 24px;
      font-size: 0.9rem;
      color: var(--text-muted);
    }
    .subject {
      margin-bottom: 28px;
    }
    .subject h2 {
      font-size: 1.2rem;
      margin-bottom: 8px;
      color: var(--primary);
      border-left: 4px solid var(--primary);
      padding-left: 8px;
    }
    .subject-description {
      margin: 0 0 10px;
      font-size: 0.9rem;
      color: var(--text-muted);
    }
    .item {
      background: var(--card-bg);
      border-radius: 10px;
      border: 1px solid var(--border);
      padding: 10px 12px;
      margin-bottom: 8px;
    }
    .item h3 {
      margin: 0 0 4px;
      font-size: 0.95rem;
    }
    .meta {
      margin: 0 0 4px;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-muted);
    }
    .summary {
      margin: 0 0 6px;
      font-size: 0.88rem;
      color: var(--text-main);
    }
    a {
      color: var(--primary);
      text-decoration: none;
      font-size: 0.85rem;
    }
    a:hover {
      text-decoration: underline;
    }
    footer {
      margin-top: 32px;
      font-size: 0.8rem;
      color: var(--text-muted);
      text-align: center;
    }
  </style>
</head>
<body>
  <header>
    <div class="container">
      <h1>CSS Current Affairs Newsletter</h1>
      <p>Dawn & The Express Tribune • Key news and op-eds • Essay-focused subjects</p>
    </div>
  </header>
  <main class="container">
"""
    )

    parts.append(f'    <p class="date">Generated on {date_str} (for personal reading / CSS prep)</p>\n')

    # Add sections per subject
    for subject in SUBJECT_ORDER:
        items = classified.get(subject, [])
        if not items:
            continue

        parts.append('    <section class="subject">\n')
        parts.append(f'      <h2>{subject}</h2>\n')

        # Short description hinting how to use for essays (optional / generic)
        parts.append(
            '      <p class="subject-description">'
            'Scan these for arguments, data points, and case studies you can plug into essays.'
            '</p>\n'
        )

        for item in items:
            parts.append('      <article class="item">\n')
            parts.append(f'        <h3>{item["title"]}</h3>\n')
            parts.append(f'        <p class="meta">{item["source"]}</p>\n')
            if item["summary"]:
                parts.append(f'        <p class="summary">{item["summary"]}</p>\n')
            parts.append(f'        <a href="{item["link"]}" target="_blank" rel="noopener noreferrer">Read full piece</a>\n')
            parts.append('      </article>\n')

        parts.append('    </section>\n')

    parts.append(
"""  </main>
  <footer>
    Curated automatically from public RSS feeds of Dawn & The Express Tribune for personal study use.
  </footer>
</body>
</html>
"""
    )

    return "".join(parts)


def main():
    print("[INFO] Fetching feeds from Dawn & The Express Tribune...")
    classified = fetch_articles()
    html = build_html(classified)
    output_file = "newsletter.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Wrote {output_file}")


if __name__ == "__main__":
    main()
