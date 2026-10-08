import sqlite3
import pandas as pd
from scipy import stats

# Connect to your SQLite database
conn = sqlite3.connect("data/cart2insights.db")

print("=" * 60)
print("📊 CART2INSIGHTS STATISTICAL HYPOTHESIS TESTING")
print("=" * 60)

# --- 1. TWO-SAMPLE T-TEST ---
# Question: Do delayed orders receive significantly lower review scores than on-time orders?
query_ttest = """
SELECT o.is_delayed, r.review_score 
FROM orders o 
JOIN reviews r ON o.order_id = r.order_id 
WHERE o.is_delayed IS NOT NULL AND r.review_score IS NOT NULL;
"""
df_ttest = pd.read_sql_query(query_ttest, conn)

delayed_scores = df_ttest[df_ttest['is_delayed'] == 1]['review_score']
ontime_scores = df_ttest[df_ttest['is_delayed'] == 0]['review_score']

t_stat, p_val_t = stats.ttest_ind(delayed_scores, ontime_scores, equal_var=False)

print("\n1️⃣ TWO-SAMPLE T-TEST: Delivery Delay vs. Review Score")
print(f"   • On-Time Orders Mean Rating : {ontime_scores.mean():.2f} ⭐")
print(f"   • Delayed Orders Mean Rating : {delayed_scores.mean():.2f} ⭐")
print(f"   • T-Statistic: {t_stat:.4f}, p-value: {p_val_t:.4e}")
if p_val_t < 0.05:
    print("   ✅ RESULT: Statistically Significant! Delivery delays significantly reduce review scores.")
else:
    print("   ❌ RESULT: No statistically significant difference found.")

# --- 2. ONE-WAY ANOVA ---
# Question: Does customer review score differ significantly across payment types?
query_anova = """
SELECT p.payment_type, r.review_score 
FROM payments p 
JOIN reviews r ON p.order_id = r.order_id 
WHERE p.payment_type IN ('credit_card', 'boleto', 'voucher', 'debit_card') 
  AND r.review_score IS NOT NULL;
"""
df_anova = pd.read_sql_query(query_anova, conn)

groups = [group['review_score'].values for _, group in df_anova.groupby('payment_type')]
f_stat, p_val_anova = stats.f_oneway(*groups)

print("\n2️⃣ ONE-WAY ANOVA: Review Score Across Payment Types")
for p_type, group in df_anova.groupby('payment_type'):
    print(f"   • {p_type.title():<12}: Mean Rating = {group['review_score'].mean():.2f} ⭐")
print(f"   • F-Statistic: {f_stat:.4f}, p-value: {p_val_anova:.4e}")
if p_val_anova < 0.05:
    print("   ✅ RESULT: Statistically Significant! Customer satisfaction varies across payment methods.")
else:
    print("   ❌ RESULT: No statistically significant difference across payment types.")

# --- 3. CHI-SQUARE TEST OF INDEPENDENCE ---
# Question: Is delivery delay independent of the customer's state (top 5 states)?
query_chisq = """
SELECT c.customer_state, o.is_delayed 
FROM orders o 
JOIN customers c ON o.customer_id = c.customer_id 
WHERE c.customer_state IN ('SP', 'RJ', 'MG', 'RS', 'PR') 
  AND o.is_delayed IS NOT NULL;
"""
df_chisq = pd.read_sql_query(query_chisq, conn)

contingency_table = pd.crosstab(df_chisq['customer_state'], df_chisq['is_delayed'])
chi2, p_val_chi2, dof, _ = stats.chi2_contingency(contingency_table)

print("\n3️⃣ CHI-SQUARE TEST: Delivery Delay vs. Customer State (Top 5 States)")
print(f"   • Chi2 Statistic: {chi2:.4f}, Degrees of Freedom: {dof}, p-value: {p_val_chi2:.4e}")
if p_val_chi2 < 0.05:
    print("   ✅ RESULT: Statistically Significant! Delivery delays are dependent on customer location.")
else:
    print("   ❌ RESULT: Delivery delay is independent of customer state.")

conn.close()
print("\n" + "=" * 60)
