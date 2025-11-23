import streamlit as st
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
        "policy rate", "sbp", "state bank", "psx", "stock market",
        "fiscal deficit", "current account", "trade deficit", "remittances",
        "business", "industry"
    ],
    "Economic Issues and Reforms": [
        "imf", "reforms", "privatisation", "privatization", "tax reform",
        "fbr", "revenue", "subsidy", "circular debt", "energy tariff",
        "structural reform", "austerity", "budget", "taxation",
    ],
    "Agriculture": [
        "agriculture", "crop", "wheat", "cotton", "rice", "sugarcane",
        "fertiliser", "fertilizer", "farmer", "livestock", "seed",
        "irrigation", "canal", "watercourse", "agri"
    ],
    "Geopolitics": [
        "geopolitics", "great power", "china", "india", "us", "russia",
        "middle east", "gulf", "saudi", "iran", "turkey", "taliban",
        "belt and road", "multipolar", "bloc", "pakistan-us",
        "pakistan-china", "pakistan-india"
    ],
    "National Security": [
        "terror", "terrorism", "militant", "ctd", "security forces",
        "army", "military", "nacta", "internal security", "insurgency",
        "balochistan unrest", "attack", "counterterrorism"
    ],
    "Foreign Policy": [
        "foreign policy", "diplomacy", "bilateral", "summit",
        "oic", "unsc", "united nations", "strategic partnership",
        "border", "kashmir", "fm", "foreign office", "fo spokesperson",
        "ambassador", "envoy"
    ],
    "Constitutional Law and Judiciary": [
        "supreme court", "sc", "high court", "lhr hc", "shc", "ihc",
        "constitution", "constitutional", "article", "basic structure",
        "judiciary", "bench", "petition", "reference", "election act",
        "law", "legal challenge"
    ],
    "Gender": [
        "women", "gender", "harassment", "violence against women",
        "domestic violence", "honour killing", "honor killing",
        "girls’ education", "women’s rights", "gender parity",
        "sexual harassment", "feminist", "patriarchy"
    ],
    "Social Issues": [
        "poverty", "inequality", "healthcare", "health care",
        "education", "literacy", "housing", "slums",
        "informal settlements", "malnutrition", "stunting",
        "public health", "epidemic", "social safety net",
        "bisp", "ehsaas", "youth", "labour", "labor rights",
        "unemployment", "minimum wage", "cost of living"
    ],
}

# -----------------------------
# RSS FEEDS (Dawn + Tribune)
# -----------------------------

FEEDS = {
    "Dawn": [
        "https://www.dawn.com/feeds/home",   # main feed :contentReference[oaicite:0]{index=0}
    ],
    "The Express Tribune": [
        "https://tribune.com.pk/rss",        # generic RSS hub feed :contentReference[oaicite:1]{index=1}
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
    """Simple keyword-based subject classification."""
    blob = (title + " " + summary).lower()
    for subject in SUBJECT_ORDER:
        for kw in SUBJECT_KEYWORDS[subject]:
            if kw.lower() in blob:
                return subject
    return None


@st.cache_data(ttl=600)
def fetch_articles(max_per_subject: int = 8):
    """Fetch and classify articles from all feeds (cached for 10 minutes)."""
    classified = {subject: [] for subject in SUBJECT_ORDER}

    for source, urls in FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                st.warning(f"Could not parse feed {url}: {e}")
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

                classified[subject].append(
                    {
                        "source": source,
                        "title": title,
                        "summary": summary,
                        "link": link,
                    }
                )

    # truncate
    for subject in SUBJECT_ORDER:
        classified[subject] = classified[subject][:max_per_subject]

    return classified


# -----------------------------
# STREAMLIT UI
# -----------------------------

def main():
    st.set_page_config(
        page_title="CSS Current Affairs Newsletter",
        page_icon="📰",
        layout="wide",
    )

    # --- HEADER ---
    st.title("📰 CSS Current Affairs Newsletter")
    st.markdown(
        """
        **Dawn + The Express Tribune** • Key News & Op-Eds • Curated for CSS essay prep.

        Use this as your **daily/weekly reading sheet** for:
        * Economy & reforms  
        * Agriculture  
        * Geopolitics, national security & foreign policy  
        * Constitutional law & judiciary  
        * Gender & social issues  
        """
    )

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.header("Settings")

        max_items = st.slider(
            "Max articles per subject",
            min_value=3,
            max_value=15,
            value=8,
        )

        selected_subjects = st.multiselect(
            "Filter subjects",
            options=SUBJECT_ORDER,
            default=SUBJECT_ORDER,
        )

        st.caption("Tip: Narrow down to 2–3 subjects when focusing on a particular paper/essay.")

        refresh = st.button("🔄 Refresh feeds")

    if refresh:
        # Clear cache and refetch
        fetch_articles.clear()

    with st.spinner("Fetching Dawn & Tribune feeds…"):
        classified = fetch_articles(max_per_subject=max_items)

    st.markdown(
        f"<p style='color:#6b7280;font-size:0.9rem;'>Updated on {datetime.now().strftime('%d %b %Y, %H:%M')}</p>",
        unsafe_allow_html=True,
    )

    # --- CONTENT ---
    for subject in SUBJECT_ORDER:
        if subject not in selected_subjects:
            continue

        articles = classified.get(subject, [])
        if not articles:
            continue

        st.markdown(f"## {subject}")
        st.markdown(
            "<p style='color:#6b7280;font-size:0.9rem;margin-top:-12px;'>"
            "Scan these for arguments, data points and case studies usable in essays."
            "</p>",
            unsafe_allow_html=True,
        )

        for art in articles:
            with st.container():
                st.markdown(
                    f"**{art['title']}**  \n"
                    f"<span style='font-size:0.75rem;color:#6b7280;text-transform:uppercase;'>"
                    f"{art['source']}</span>",
                    unsafe_allow_html=True,
                )
                if art["summary"]:
                    st.write(art["summary"])
                st.markdown(
                    f"[Read full piece ↗]({art['link']})",
                    help="Opens in a new tab",
                )
                st.markdown("---")


if __name__ == "__main__":
    main()
