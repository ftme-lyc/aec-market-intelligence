import streamlit as st
import pandas as pd
import re
from newspaper import Article
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from difflib import SequenceMatcher
from aec_agent import normalize_signal_strength, run_news_insight_agent, ultimate_aec_market_intelligence_prompt, rss_feeds
from azure_storage import load_insights_from_blob, upload_insights_to_blob



st.set_page_config(page_title="AEC Market Intelligence Dashboard", layout="wide")

st.title("🏗️ AEC Market Intelligence Dashboard")

# Load insights CSV
def get_predefined_data():
    df = load_insights_from_blob()
    if not df.empty:
        return df
    else:
        manual_pages = ["SkyResidenceDawson"]
        df = run_news_insight_agent(rss_feeds, manual_pages=manual_pages)
        upload_insights_to_blob(df)  
        return df

df = get_predefined_data()


st.sidebar.header("🔎 Analyze an Article")
user_url = st.sidebar.text_input(label="Add an Article...", placeholder="Paste a single news article link here")

        
st.sidebar.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

parsed = None
custom_result = None
if user_url:
    with st.spinner("Extracting insights..."):
        try:
            article = Article(user_url)
            article.download()
            article.parse()

            title = article.title
            summary = article.text[:500]  

            insight = ultimate_aec_market_intelligence_prompt(title, summary)

            parsed = {
                "Source": "User Input", "Title": title, "URL": user_url, "raw_insight": insight,
                "Summary": summary, "Source Type": "", "Category": "", "Entity Involved": "", "City": "", "Country": "", "Sector": "",
                "Project or Initiative Name": "", "Project Status": "", "Strategic Insight Summary": "",
                "Signal Strength": "", "Action Recommendation": ""
            }

            for line in insight.splitlines():
                match = re.match(r"\d+\.\s+\*\*(.*?)\*\*:\s*(.*)", line)
                if match:
                    key, value = match.groups()
                    if value.endswith('.'):
                        value = value[:-1]
                    if key == "Signal Strength":
                        value = normalize_signal_strength(value)
                    if key in parsed:
                        parsed[key] = value.strip()
                    

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Similarity checker
def is_duplicate_summary(new_summary, existing_summaries, threshold=0.8):
    for summary in existing_summaries:
        similarity = SequenceMatcher(None, new_summary, summary).ratio()
        if similarity > threshold:
            return True
    return False

if parsed is not None:
    new_summary = parsed["Summary"]

    # Handle case when custom_result is None or empty
    if custom_result is None or custom_result.empty:
        custom_result = pd.DataFrame([parsed])
        st.success("Insight added!")
    else:
        existing_summaries = df["Summary"].tolist()
        if not is_duplicate_summary(new_summary, existing_summaries):
            custom_result = pd.concat([custom_result, pd.DataFrame([parsed])], ignore_index=True)
            st.success("Insight added!")
        else:
            st.warning("⚠️ Similar insight already exists. Skipping duplicate entry.")

if custom_result is not None:
    df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)

# if parsed is not None:
#     new_summary = parsed["Summary"]
#     existing_summaries = df["Summary"].tolist() if not df.empty else []

#     if not is_duplicate_summary(new_summary, existing_summaries):
#         new_row = pd.DataFrame([parsed])
#         custom_result = pd.concat([custom_result, new_row], ignore_index=True)
#         df = pd.concat([df, new_row], ignore_index=True)
#         st.success("✅ Insight added!")
#     else:
#         st.warning("⚠️ Similar insight already exists. Skipping duplicate entry.")

    # if is_duplicate_summary(new_summary, existing_summaries):
    #     st.warning("⚠️ Similar insight already exists. Skipping duplicate entry.")
    # else:
    #     # Add to custom_result
    #     if custom_result is None or custom_result.empty:
    #         custom_result = pd.DataFrame([parsed])
    #     else:
    #         custom_result = pd.concat([custom_result, pd.DataFrame([parsed])], ignore_index=True)

    #     # Add to df
    #     df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)
    #     st.success("Insight added!")



# Filters
with st.sidebar:
    st.markdown("""
    <div style='font-size: 1.2rem; font-weight: 600; margin-bottom: -15px; margin-top:10px'>🗂️ Filter Insights</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-top:10px; margin-bottom:-200px">
        <strong>Sector</strong> <span style='font-size: 0.8em; color: gray;'>(e.g. Construction, Hospitality)</span>
    </div>
    """, unsafe_allow_html=True)
    selected_sector = st.multiselect("", options=df["Sector"].dropna().unique())

    st.markdown("""
    <div style="margin-bottom:-40px; margin-top:10px">
        <strong>Category</strong> <span style='font-size: 0.8em; color: gray;'>(e.g. Project Win, Policy Update)</span>
    </div>
    """, unsafe_allow_html=True)
    selected_category = st.multiselect("", options=df["Category"].dropna().unique())

    st.markdown("""
    <div style="margin-bottom:-40px; margin-top:10px">
        <strong>Signal Strength</strong> <span style='font-size: 0.8em; color: gray;'>(High, Medium, Low)</span>
    </div>
    """, unsafe_allow_html=True)
    selected_signal = st.multiselect("", options=df["Signal Strength"].dropna().unique())

# Apply filters
filtered_df = df.copy()
if selected_sector:
    filtered_df = filtered_df[filtered_df["Sector"].isin(selected_sector)]
if selected_category:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_category)]
if selected_signal:
    filtered_df = filtered_df[filtered_df["Signal Strength"].isin(selected_signal)]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Insights", len(filtered_df))
col2.metric("High Signal Entries", sum(filtered_df["Signal Strength"] == "High"))
col3.metric("Unique Entities", filtered_df["Entity Involved"].nunique())

# Insights by Location
st.subheader("📍 Insights by Location")
filtered_df["Location"] = filtered_df["City"].fillna("Unknown") + ", " + filtered_df["Country"].fillna("Unknown")
location_data = filtered_df[filtered_df["Location"] != "Unknown, Unknown"]
location_counts = location_data["Location"].value_counts().reset_index()
location_counts.columns = ["Location", "Count"]
fig_location = px.bar(location_counts, x="Location", y="Count")
st.plotly_chart(fig_location, use_container_width=True)

# Geographic Distribution
st.subheader("🌍 Geographic Distribution")
size_map = {
    "Low": 2,
    "Medium": 5,
    "High": 10
}
location_data["Signal Score"] = location_data["Signal Strength"].map(size_map).fillna(8)

fig_geographic = px.scatter_geo(
    location_data,
    locations="Country",
    locationmode="country names",
    hover_name="City",
    color="Sector",  
    size="Signal Score",         
    projection="natural earth"  
)

fig_geographic.update_layout(
    geo=dict(
        showland=True,
        landcolor="rgba(240, 240, 240, 1)",  
        bgcolor="rgba(0,0,0,0)", 
        showocean=True,
        oceancolor="rgba(230, 240, 250, 1)",  
        showcountries=True,
        showframe=False,
    ),
    margin=dict(l=0, r=0, t=40, b=0),  
    height=600
)

st.plotly_chart(fig_geographic, use_container_width=True)

# Sector Distribution
st.subheader("🏷️ Sector Distribution")
fig_sector = px.pie(filtered_df, names="Sector")
st.plotly_chart(fig_sector, use_container_width=True)

# WordCloud
st.subheader("💬 Emerging Client Priorities (from Strategic Insights)")

custom_stopwords = set(STOPWORDS).union({
    "this", "that", "it", "they", "may", "must", "new", "within", "due", "including",
    "completion", "similar", "position", "article", "lead", "prepare",
    "project", "projects", "design", "opportunity", "opportunities", "potential",
    "priority", "priorities", "highlight", "highlights", "signals", "shift",
    "focus", "trend", "significant", "underscores",
    "sj", "surbana", "jurong", "firm", "firms", "consultancy", "contractors", "entrants",
    "region", "requirements", "rules", "companies", "framework", "solution", "solutions",
    "u.s.", "african", "tanzania", "east", "social"
})
text = " ".join(filtered_df["Strategic Insight Summary"].dropna()).lower()
words = [word for word in text.split() if word not in custom_stopwords]
word_freq = Counter(words)

wc = WordCloud(
    width=600, height=300,
    background_color="white",
    colormap="tab10",
    max_words=100, 
    random_state=42
).generate_from_frequencies(word_freq)

fig_WordCloud, ax = plt.subplots(figsize=(7, 4))
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig_WordCloud)

wc.to_file("wordcloud_trends.png")

with open("wordcloud_trends.png", "rb") as img_file:
    st.download_button(label="Download Word Cloud as PNG", data=img_file, file_name="client_priorities_wordcloud.png", mime="image/png")

# Table of Insight from Submitted Article
if custom_result is not None and not custom_result.empty:
    st.subheader("📄 View Insight from Submitted Article")
    with st.expander("Click to view the insight"):
        st.dataframe(custom_result[[
                "Title", "Source Type", "Entity Involved", "Category", "Summary", 
                "Project Status", "Country", "City", "Sector", "Project or Initiative Name",
                "Signal Strength", "Strategic Insight Summary", "Action Recommendation"
        ]])

st.subheader("🧠 Strategic Insights and Recommended Actions")
st.dataframe(filtered_df[["Title", "Source Type", "Entity Involved", "Category", "Summary", "Project Status", "Country", "City", "Sector", "Strategic Insight Summary", "Action Recommendation"]])

st.download_button("Download Strategic Insights", data=filtered_df.to_csv(index=False), file_name="Strategic Insights.csv", mime="text/csv")

# Regulatory Impact Analysis
st.subheader("📜 Regulatory Impact Analysis")
regulatory_df = filtered_df[
    (filtered_df["Category"] == "Policy/Regulatory Update") &
    (filtered_df["Source Type"] != "Internal")
]
if not regulatory_df.empty:
    st.dataframe(regulatory_df[[
        "Title", "Country", "Sector", "Project Status",
        "Strategic Insight Summary", "Action Recommendation"
    ]].reset_index(drop=True))
else:
    st.info("No regulatory updates detected in the current data.")

reg_sector_counts = regulatory_df["Sector"].value_counts().reset_index()
reg_sector_counts.columns = ["Sector", "Policy Mentions"]

fig_reg = px.bar(
    reg_sector_counts,
    x="Sector", y="Policy Mentions",
    title="Sectors Most Affected by Regulatory Activity",
    color="Sector"
)
st.plotly_chart(fig_reg, use_container_width=True)


# High-Potential Early Market Leads
show_high_signal_early = st.sidebar.checkbox("🚨 Show High-Potential Leads Only", value=False)
if show_high_signal_early:
    filtered_df = df[
        (df["Category"] == "Early Market Signal") &
        (df["Signal Strength"] == "High") &
        (df["Source Type"] != "Internal")
    ]
    def flag_lead(row):
        if row["Category"] == "Early Market Signal" and row["Signal Strength"] == "High" and row["Source Type"] != "Internal":
            return "🔥 High Potential"
        return ""

    filtered_df["Lead Flag"] = filtered_df.apply(flag_lead, axis=1)

    if not filtered_df.empty:
        st.success(f"{len(filtered_df)} high-potential opportunities detected.")
        
        st.subheader("🚨 High-Potential Early Market Leads")
        st.dataframe(filtered_df[[
            "Title", "Entity Involved", "Category", "Sector", "City", "Country",
            "Signal Strength", "Strategic Insight Summary", "Action Recommendation"
        ]].reset_index(drop=True))
        st.download_button("Download High-Potential Opportunities", data=filtered_df.to_csv(index=False), file_name="High Potential Insights.csv", mime="text/csv")


upload_insights_to_blob(df)