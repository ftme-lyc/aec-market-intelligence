# 🏗️ AEC Market Intelligence Dashboard

This project is a Streamlit-based AI-powered dashboard designed to help Architecture, Engineering, and Construction (AEC) firms like **Surbana Jurong** gain a strategic edge through real-time news monitoring, insight extraction, and opportunity detection.

It uses **Azure OpenAI**, **web scraping**, and **NLP agents** to analyze industry publications and visualize emerging trends, regulatory changes, and high-potential project leads.

---

## 🔗 Live Demo
**Streamlit App**: []()

## 🎯 Use Case
This dashboard helps strategy and business development teams:
- Stay ahead of competitors by spotting early market trends
- Visualize market activity by region and sector
- Align resources to the most promising business leads
- Understand regulatory movements affecting future opportunities

## 🚀 Key Features

- ✅ **AI Agent for Insight Extraction**
  - Analyzes industry news from RSS feeds and article links
  - Extracts structured intelligence (e.g. Category, Sector, Signal Strength)

- 📊 **Interactive Dashboard**
  - Filter insights by Sector, Category, Signal Strength
  - KPIs for volume, signal levels, and entities
  - Sector-wise pie chart, geo maps, and location bar charts

- 🌍 **Geographic & Sectoral Visualization**
  - Map of insights by country and city
  - Pie chart showing sector distribution

- 💬 **Emerging Client Priorities**
  - Word cloud based on strategic insights to show market focus areas

- 📜 **Regulatory Impact Analysis**
  - Highlights sectors most impacted by policy updates

- 🚨 **High-Potential Early Market Leads**
  - Flags strong early signals for upcoming tenders or opportunities

---

## 🧠 Technologies Used

| Component                  | Tech Stack                        |
|---------------------------|-----------------------------------|
| AI/NLP Agent              | Azure OpenAI (GPT-4o)             |
| Backend & ETL             | Python, feedparser, newspaper3k   |
| Dashboard UI              | Streamlit, Plotly                 |
| Visualization             | matplotlib, wordcloud, Plotly     |
| Cloud Storage             | Azure Blob Storage                |
| Environment Variables     | python-dotenv                     |

---

## 🛠️ How to Run Locally

1. **Clone this repo:**
   ```bash
   git clone https://github.com/your-username/aec-intelligence-dashboard.git
   cd aec-intelligence-dashboard
2. **Add your .env file with Azure keys:**
   ```bash
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_BLOB_CONNECTION_STRING=your_connection_string
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
4. **Run the app:**
   ```bash
   streamlit run app.py

## 📂 File Structure
- streamlit_dashboard.py  – Main Streamlit dashboard UI with filters, visualizations, and insight submission
- aec_agent.py            – Core AI agent logic for parsing articles and extracting structured AEC insights using Azure OpenAI
- azure_storage.py        – Functions to load from and upload insights to Azure Blob Storage
- .env                    – Environment variables for API keys and credentials
- requirements.txt        – Python dependencies required to run the app
- SkyResidenceDawson.txt  – Example internal document used for manual insight parsing
- README.md               – Project overview, setup instructions, and usage documentation
