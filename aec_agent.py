import pandas as pd
import feedparser
from openai import AzureOpenAI
import time
import re
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import requests
import chardet

load_dotenv()  

rss_feeds = {
    "Construction Dive": "https://www.constructiondive.com/feeds/news/",
    "Dezeen Architecture": "https://www.dezeen.com/architecture/feed/",
    "Architect Magazine": "https://www.architectmagazine.com/rss/",
    "ArchDaily": "https://www.archdaily.com/rss",
    "Global Construction Review": "https://www.globalconstructionreview.com/feed/",
}

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),                     
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),        
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2023-05-15"                       
)

def ultimate_aec_market_intelligence_prompt(title, summary=None):
    prompt = f"""
You are a senior market intelligence agent with expert knowledge of the Architecture, Engineering, and Construction (AEC) industry. 
You have one goal: to extract deep, actionable insights from industry articles, publications, and announcements to support proactive business development and strategic positioning for Surbana Jurong.

You will be given a news article title{'' if not summary else ' and summary'} from a professional AEC-relevant source. 
You may receive either:
a. An external article title and/or summary (e.g., industry news, announcements, regulations), or
b. An internal record (e.g., past SJ project, strategic document, or portfolio entry).

Your task is to analyse the article and extract structured intelligence in the format below. 
If a field does not apply (e.g., Action Recommendation for a completed SJ project), return "N/A".
If any words in your output appear garbled, misencoded, or unreadable (e.g., 'xÆ°á»Ÿng xÃ©p', 'â€™'), rewrite them with the correct English equivalent.

Return your findings in the following exact format:

1. **Summary**: Provide a clear one- or two-sentence summary of the article content.
2. **Source Type**: Indicate if the source is External or Internal.
3. **Is this relevant to the AEC industry?** (Yes/No). If "No", stop here.
4. **Category**: Classify the main theme of the article. Choose from:
   - Project Win
   - Strategic Movement
   - Competitor Activity
   - Policy/Regulatory Update
   - Early Market Signal
   - Historical SJ Project
   - Strategic Plan (Internal)
5. **Entity Involved**: Name the main company, government agency, or organization involved. Use "Surbana Jurong" for internal SJ projects. If not mentioned, write "Unknown".
6. **City**: State the city related to the project. If explicitly mentioned, extract it. If not, infer it from context (e.g., project name, company HQ, region), but return only the city name. Use a standard, full city name. Only return "Unknown" if it truly cannot be inferred. Always use a consistent, standard city name across all entries.
7. **Country**: Provide the full country name. If not explicitly stated, infer it from the city, company, or project context. Use full names (e.g., "United States", not "USA"). Return "Unknown" only if it cannot be reasonably inferred. Always use a consistent, standard country name across all entries.
8. **Sector**: Identify the AEC sector involved (e.g., Transport, Health, Education, Residential, Energy, Infrastructure, Urban Development).
9. **Project or Initiative Name** (if available): Name of the specific project, proposal, or initiative referenced.
10. **Project Status**: Always choose from Ongoing, Planned, Announced, Approved, Under Construction, Completed, or Unclear.
11. **Strategic Insight Summary**: In 1–2 sentences, explain why this source is strategically important.
If the source is external (e.g., news article, competitor update, regulation), highlight its implications for market opportunity, client priorities, competitive positioning, or business development (e.g., potential RFP, strategic trend, partnership signal).
If the source is internal (e.g., historical SJ project or strategic plan), summarize its relevance to SJ’s market credibility, capabilities, or lessons learned that can inform future pursuits.
12. **Signal Strength** (Low / Medium / High): Rate how strong this article is as a market signal for new project opportunity or strategic shift. For external sources only. Use "N/A" for internal data.
13. **Action Recommendation**: Suggest what a strategic growth or BD team at Surbana Jurong should do next (e.g., monitor, reach out, position for bid, form a partnership, conduct further research). If historical/internal and no action is needed, return "N/A".

Be concise and complete all of the fields. Do not end any field with a period (.). 
Always return clean, fluent English.

Article Title: "{title}"
{f"Article Summary: {summary}" if summary else ''}
"""

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "You are an elite AEC strategy analyst producing executive-grade insights for proactive business growth."
             "If any words in the title or summary appear garbled, corrupted, or misencoded (e.g., 'â€™', 'xÃ©p'), attempt to infer and rewrite them correctly. "
             "Translate foreign terms or Unicode errors into their likely English equivalents."
             "Every field must be completed exactly as listed. Use 'N/A' only if the source is an internal article and the field is not applicable."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=800
    )

    return response.choices[0].message.content.strip()


def normalize_signal_strength(value):
    value = value.lower().strip().rstrip('.') 
    if value == "high":
        return "High"
    elif value == "medium":
        return "Medium"
    elif value == "low":
        return "Low"
    return value.capitalize()

def extract_clean_feed_entry(entry):
    try:
        res = requests.get(entry.link, timeout=10)
        detected = chardet.detect(res.content)
        html = res.content.decode(detected["encoding"], errors="replace")
        soup = BeautifulSoup(html, 'html.parser')

        paragraphs = soup.find_all('p')
        full_summary = " ".join(p.get_text() for p in paragraphs[:3])

        title = entry.title
        return {
            "title": title.strip(),
            "summary": full_summary.strip()
        }
    except Exception as e:
        print(f"❌ Failed to extract full text from {entry.link}: {e}")
        return {
            "title": entry.title,
            "summary": entry.get("summary", "")
        }

def run_news_insight_agent(feed_dict, manual_pages=None, max_per_feed=5):
    all_results = []

    for source, url in feed_dict.items():
        feed = feedparser.parse(url)
        print(f"\n📡 Processing: {source}")

        for entry in feed.entries[:max_per_feed]:
            article = extract_clean_feed_entry(entry)
            title = article["title"]
            summary = article["summary"]


            insight = ultimate_aec_market_intelligence_prompt(title, summary)
            print(f"📰 {title}")
            print(f"🧠 Output:\n{insight}\n")


            parsed_fields = {
                "Summary": None,
                "Source Type": None,
                "Category": None,
                "Entity Involved": None,
                "City": None,
                "Country": None,
                "Sector": None,
                "Project or Initiative Name": None,
                "Project Status": None,
                "Strategic Insight Summary": None,
                "Signal Strength": None,
                "Action Recommendation": None
            }

            for line in insight.splitlines():
                match = re.match(r"\d+\.\s+\*\*(.*?)\*\*:\s*(.*)", line)
                if match:
                    key, value = match.groups()
                    key = key.strip()

                    if value.endswith('.'):
                        value = value[:-1]

                    if key == "Signal Strength":
                        value = normalize_signal_strength(value)

                    if key in parsed_fields:
                        parsed_fields[key] = value.strip()

            result = {
                "Source": source,
                "Title": title,
                "URL": entry.link,
                "raw_insight": insight,
                **parsed_fields
            }

            all_results.append(result)
            time.sleep(1.5)
 

    if manual_pages:
        for name in manual_pages:
            print(f"\n📄 Processing manual file: {name}")
            try:
                file_path = f"{name}.txt"
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                title = name.replace("_", " ")
                summary = text[:500]
                insight = ultimate_aec_market_intelligence_prompt(title, summary)
                print(f"🧠 Output:\n{insight}\n")

                parsed_fields = {
                    "Summary": None,
                    "Source Type": "Internal",
                    "Category": None,
                    "Entity Involved": "Surbana Jurong",
                    "City": None,
                    "Country": None,
                    "Sector": None,
                    "Project or Initiative Name": None,
                    "Project Status": None,
                    "Strategic Insight Summary": None,
                    "Signal Strength": None,
                    "Action Recommendation": None
                }

                for line in insight.splitlines():
                    match = re.match(r"\d+\.\s+\*\*(.*?)\*\*:\s*(.*)", line)
                    if match:
                        key, value = match.groups()
                        key = key.strip()
                        value = value.rstrip('.').strip()
                        if key == "Signal Strength":
                            value = normalize_signal_strength(value)
                        if key in parsed_fields:
                            if not parsed_fields[key]:  # Only overwrite if it was still None
                                parsed_fields[key] = value

                result = {
                    "Source": name,
                    "Title": title,
                    "URL": "Manual Upload",
                    "raw_insight": insight,
                    **parsed_fields
                }

                all_results.append(result)

            except Exception as e:
                print(f"❌ Failed to process {name}.txt: {e}")

    return pd.DataFrame(all_results)



