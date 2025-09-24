import os
import re
import streamlit as st
import matplotlib.pyplot as plt
from tavily import TavilyClient   # ✅ correct import
from dotenv import load_dotenv
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# Load API Key from .env
# -------------------------------
load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    st.error("❌ Tavily API key not found! Please check your .env file.")
    st.stop()

client = TavilyClient(api_key=api_key)   # ✅ correct initialization

# -------------------------------
# Helper functions
# -------------------------------
def clean_name(text):
    """Extracts a clean competitor name from messy titles."""
    return re.split(r"\||-|:", text)[0].strip()

def tavily_search(query, max_results=5):
    """Search using Tavily API and return summarized results."""
    try:
        result = client.search(query=query, max_results=max_results)
        return result.get("results", [])
    except Exception as e:
        return [{"title": "Error", "content": str(e)}]

def extract_price(text):
    """Extract numeric PKR price if available in text."""
    match = re.search(r"(\d{2,6})", text.replace(",", ""))
    if match:
        return int(match.group(1))
    return None

def market_research(product_name):
    """Perform multi-step research for a product."""
    competitors_query = f"Top smartwatches competing with {product_name} in 2025"
    competitors_data = tavily_search(competitors_query)
    competitors = [clean_name(item["title"]) for item in competitors_data[:3]]

    report = {"competitors": []}

    for comp in competitors:
        comp_data = {"name": comp, "features": [], "price": [], "reviews": [], "avg_price": None}

        # Features
        features = tavily_search(f"{comp} smartwatch features 2025")
        comp_data["features"] = [f["title"] + ": " + f["content"][:120] for f in features]

        # Price
        price_results = tavily_search(f"{comp} smartwatch price in Pakistan 2025 PKR")
        comp_data["price"] = [p["title"] + ": " + p["content"][:120] for p in price_results]

        # Try extracting a number for summary
        extracted_prices = [extract_price(p.get("content", "")) for p in price_results]
        extracted_prices = [p for p in extracted_prices if p]
        if extracted_prices:
            comp_data["avg_price"] = sum(extracted_prices) // len(extracted_prices)

        # Reviews
        reviews = tavily_search(f"{comp} smartwatch customer reviews 2025")
        comp_data["reviews"] = [r["title"] + ": " + r["content"][:120] for r in reviews]

        report["competitors"].append(comp_data)

    return report

def generate_pdf(report, product_name):
    """Generate PDF report from research data."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"📊 Market Analysis Report — {product_name}", styles['Heading1']))
    story.append(Spacer(1, 12))

    for comp in report["competitors"]:
        story.append(Paragraph(f"🔎 Competitor: {comp['name']}", styles['Heading2']))

        if comp["avg_price"]:
            story.append(Paragraph(f"💰 Estimated Avg Price: PKR {comp['avg_price']:,}", styles['Normal']))

        story.append(Paragraph("Key Features:", styles['Heading3']))
        for f in comp["features"]:
            story.append(Paragraph("• " + f, styles['Normal']))

        story.append(Paragraph("Prices:", styles['Heading3']))
        for p in comp["price"]:
            story.append(Paragraph("• " + p, styles['Normal']))

        story.append(Paragraph("Customer Reviews:", styles['Heading3']))
        for r in comp["reviews"]:
            story.append(Paragraph("• " + r, styles['Normal']))

        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="📊 Market Research Agent", layout="wide")
st.title("📊 Market Research Agent")
st.markdown("This app researches smartwatch competitors using Tavily API and generates a structured market analysis report with *charts & graphs*.")

# Sidebar Controls
st.sidebar.header("⚙️ Settings")
max_tokens = st.sidebar.slider("Max Tokens", 100, 2000, 500, step=50)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, step=0.1)

# Product input
product_name = st.text_input("🔎 Enter Product Name:", "Nexus Smartwatch Pro 2")

if st.button("Run Research"):
    with st.spinner("Researching live market data... ⏳"):
        report = market_research(product_name)

        st.success(f"✅ Market Research Completed for {product_name}")

        # ---- Display Competitors ----
        avg_prices = {}
        for comp in report["competitors"]:
            with st.expander(f"📌 {comp['name']}"):
                if comp["avg_price"]:
                    st.caption(f"💰 Estimated Avg Price: PKR {comp['avg_price']:,}")
                    avg_prices[comp["name"]] = comp["avg_price"]

                st.subheader("Key Features")
                for f in comp["features"]:
                    st.write("- " + f)

                st.subheader("Price in PKR")
                for p in comp["price"]:
                    st.write("- " + p)

                st.subheader("Customer Sentiment")
                for r in comp["reviews"]:
                    st.write("- " + r)

        # ---- Price Comparison Bar Chart ----
        if avg_prices:
            st.subheader("📊 Price Comparison Chart")
            fig, ax = plt.subplots()
            ax.bar(avg_prices.keys(), avg_prices.values())
            ax.set_ylabel("Price (PKR)")
            ax.set_title("Average Price Comparison of Competitors")
            st.pyplot(fig)

        # ---- Fake Sentiment Pie Chart Example ----
        st.subheader("🧭 Customer Sentiment Overview (Example Data)")
        sentiment_labels = ["Positive", "Neutral", "Negative"]
        sentiment_values = [60, 25, 15]  # Static demo values (future: NLP analysis)

        fig2, ax2 = plt.subplots()
        ax2.pie(sentiment_values, labels=sentiment_labels, autopct='%1.1f%%')
        ax2.set_title("Customer Sentiment Distribution")
        st.pyplot(fig2)

        # ---- PDF Download Button ----
        pdf_buffer = generate_pdf(report, product_name)
        st.download_button(
            label="📥 Download Report as PDF",
            data=pdf_buffer,
            file_name=f"{product_name.replace(' ', '_')}_Market_Report.pdf",
            mime="application/pdf",
        )
