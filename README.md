📊 Market Research Agent

A **Streamlit-based Market Research Tool** powered by the **Tavily API**.  
This app fetches live competitor data (features, prices, reviews), generates charts, and creates a downloadable PDF report.

---

## 🚀 Features  

- **Live Market Research** – Fetch up-to-date competitor info using Tavily API  
- **Competitor Extraction** – Automatically identifies top smartwatches  
- **Feature Analysis** – Collect product highlights and specifications  
- **Price Insights** – Extracts numeric prices and calculates average price in PKR  
- **Customer Reviews** – Summarizes online customer reviews  
- **Data Cleaning** – Cleans competitor names and removes extra text  
- **Visualizations** –  
  - Bar chart: Competitor price comparison  
  - Pie chart: Customer sentiment overview (example/demo)  
- **PDF Report Generator** – One-click export of structured market research report  
- **Customizable Settings** – Adjust max tokens & temperature in sidebar  
- **Interactive UI** – Expand competitor details using Streamlit expanders  

---

## 🛠️ Tech Stack  

- **Python 3.10+**  
- **Streamlit** – Web app frontend  
- **Tavily API (`tavily-python`)** – Live market research  
- **Matplotlib** – Data visualization (charts)  
- **ReportLab** – PDF generation  
- **dotenv** – Secure API key management