# Cart2Insights: E-Commerce Data & Analytics Capstone

## Statistical Analysis Results

Summary outputs from the hypothesis tests are saved to `results/statistical_results.txt`.

Highlights:
- Delivery delays significantly reduce customer review scores.
- Customer satisfaction varies across payment methods (ANOVA significant).
- Delivery delays are associated with customer location (Chi-square significant).

To reproduce, run:

```
/Users/gayu8/Desktop/Cart2Insights/.venv/bin/python 02_statistical_analysis.py
```

# Cart2Insights: E-Commerce Data & Analytics Capstone

## 📌 Project Overview
An end-to-end data analytics pipeline and interactive Streamlit dashboard analyzing e-commerce transactions across customer distribution, sales performance, delivery logistics, payment channels, and statistical hypothesis testing.

This capstone project brings together data cleaning, SQL-based storage, exploratory analysis, and statistical inference to uncover actionable insights from transactional e-commerce data.

## 🛠️ Tech Stack
- Language: Python 3.12
- Database: SQLite (`cart2insights.db`)
- Data Processing: Pandas, SQLAlchemy
- Statistics: SciPy (`scipy.stats`)
- Visualization & App: Streamlit, Plotly Express

## 🔬 Key Statistical Findings
1. Two-Sample T-Test (Delivery Delay vs. Review Score): p < 0.05. Delayed orders experience statistically significant lower review ratings.
2. One-Way ANOVA (Review Score across Payment Types): p < 0.05. Customer review scores vary significantly depending on the payment method used.
3. Chi-Square Test of Independence (Delivery Delay vs. Location): p < 0.05. Delivery delays are strongly dependent on the customer's state/location.

## 🚀 How to Run the Project
1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit dashboard:
   ```bash
   streamlit run app.py
   ```

4. Open the local URL displayed in the terminal in your browser.

## 📊 What the Dashboard Covers
- Customer distribution by state and region
- Sales performance by product category and order value
- Delivery delay analysis and logistics insights
- Payment method trends and review-score comparisons
- Statistical testing outputs for business decision-making

## 🧠 Project Workflow
- Load raw e-commerce data
- Clean and transform data with Pandas
- Store processed data in SQLite
- Run descriptive and inferential analysis
- Visualize results in a Streamlit dashboard
- Interpret metrics to support business recommendations

## 📁 Project Structure
```text
Cart2Insights/
├── app.py
├── data/
├── notebooks/
├── requirements.txt
├── README.md
├── cart2insights.db
└── .venv/
```

## ✅ Outcome
The project produces a practical analytics workflow that combines structured data engineering with statistical validation, creating a business-friendly dashboard for understanding performance drivers in an e-commerce ecosystem.
