"""
FUNDAMENTAL DATA ANALYST - DECISION TREE PROJECT
PART 1: BUSINESS & DATA UNDERSTANDING

Dataset: Kasus Bunuh Diri di Jawa Barat (2019-2024)
Focus: Binary Classification dengan Decision Tree
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*70)
print("DECISION TREE PROJECT - BUSINESS & DATA UNDERSTANDING")
print("="*70)

# ============================================
# 1. BUSINESS UNDERSTANDING
# ============================================

print("\n" + "="*70)
print("BUSINESS UNDERSTANDING")
print("="*70)

business_context = """
KONTEKS BISNIS:
Kasus bunuh diri merupakan masalah kesehatan mental yang serius di Jawa Barat.
Data menunjukkan distribusi kasus yang sangat tidak merata antar wilayah.
Pemerintah membutuhkan sistem untuk mengidentifikasi wilayah berisiko.

PROBLEM STATEMENT:
Bagaimana mengidentifikasi wilayah yang berpotensi mengalami kasus bunuh diri
untuk alokasi sumber daya pencegahan yang lebih efektif?

TUJUAN PROJECT:
1. Mengembangkan model klasifikasi untuk prediksi risiko wilayah
2. Mengidentifikasi faktor-faktor yang paling berpengaruh
3. Memberikan rekomendasi berbasis data untuk intervensi preventif

PENDEKATAN: BINARY CLASSIFICATION
Target: Wilayah "Berisiko" vs "Tidak Berisiko"
- Berisiko: Wilayah dengan jumlah kasus > 0
- Tidak Berisiko: Wilayah dengan 0 kasus

ALGORITMA: DECISION TREE
Dipilih karena:
✅ Interpretable - mudah dijelaskan ke stakeholder non-teknis
✅ Handle imbalanced data dengan class weights
✅ Dapat handle non-linear relationships
✅ Feature importance analysis built-in
✅ Robust to outliers
✅ Tidak perlu feature scaling

SUCCESS CRITERIA:
- Precision > 60% (minimize false alarms)
- Recall > 50% (detect actual risk areas)
- F1-Score > 55% (balance precision & recall)
- ROC-AUC > 0.70 (overall discrimination ability)
- Model interpretability tinggi untuk decision support
"""

print(business_context)

# ============================================
# 2. LOAD & EXPLORE DATA
# ============================================

print("\n" + "="*70)
print("DATA LOADING & INITIAL EXPLORATION")
print("="*70)

# Load dataset
df = pd.read_csv('jml_kejadian_bunuh_diri__des_kel.csv')

print(f"\n[DATASET OVERVIEW]")
print("-" * 70)
print(f"Total Records: {len(df):,}")
print(f"Total Features: {len(df.columns)}")
print(f"Periode: {df['tahun'].min()} - {df['tahun'].max()}")
print(f"Jumlah Tahun: {df['tahun'].nunique()}")

print(f"\n[GEOGRAPHIC COVERAGE]")
print("-" * 70)
print(f"Provinsi: {df['nama_provinsi'].nunique()}")
print(f"Kabupaten/Kota: {df['bps_nama_kabupaten_kota'].nunique()}")
print(f"Kecamatan: {df['bps_nama_kecamatan'].nunique()}")
print(f"Desa/Kelurahan: {df['bps_nama_desa_kelurahan'].nunique()}")

print(f"\n[COLUMNS]")
print("-" * 70)
print(df.columns.tolist())

print(f"\n[DATA TYPES]")
print("-" * 70)
print(df.dtypes)

print(f"\n[MISSING VALUES]")
print("-" * 70)
missing = df.isnull().sum()
if missing.sum() == 0:
    print("✅ NO MISSING VALUES")
else:
    print(missing[missing > 0])

print(f"\n[SAMPLE DATA]")
print("-" * 70)
print(df.head(10))

# ============================================
# 3. TARGET VARIABLE ANALYSIS
# ============================================

print("\n" + "="*70)
print("TARGET VARIABLE ANALYSIS (jumlah_kejadian)")
print("="*70)

print(f"\n[DESCRIPTIVE STATISTICS]")
print("-" * 70)
print(df['jumlah_kejadian'].describe())

print(f"\n[DISTRIBUTION ANALYSIS]")
print("-" * 70)
print(df['jumlah_kejadian'].value_counts().head(15))

# Calculate key metrics
total_records = len(df)
zero_cases = (df['jumlah_kejadian'] == 0).sum()
non_zero_cases = (df['jumlah_kejadian'] > 0).sum()
pct_zero = zero_cases / total_records * 100
pct_non_zero = non_zero_cases / total_records * 100

print(f"\n[CLASS DISTRIBUTION]")
print("-" * 70)
print(f"Tidak Ada Kasus (0): {zero_cases:,} ({pct_zero:.2f}%)")
print(f"Ada Kasus (>0):      {non_zero_cases:,} ({pct_non_zero:.2f}%)")
print(f"\n⚠️ SEVERE CLASS IMBALANCE DETECTED!")
print(f"   Ratio = {zero_cases/non_zero_cases:.1f}:1")

# ============================================
# 4. VISUALIZATIONS
# ============================================

print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70)

# [A] Class Distribution Pie Chart
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Target Variable Analysis', fontsize=16, fontweight='bold')

# Pie chart
colors = ['lightcoral', 'lightgreen']
axes[0, 0].pie([zero_cases, non_zero_cases], 
               labels=['Tidak Ada Kasus (0)', 'Ada Kasus (>0)'],
               autopct='%1.2f%%', colors=colors, startangle=90,
               textprops={'fontsize': 11, 'fontweight': 'bold'})
axes[0, 0].set_title('Class Distribution (Binary)', fontsize=13, fontweight='bold')

# Bar chart
axes[0, 1].bar(['Tidak Berisiko\n(0 kasus)', 'Berisiko\n(>0 kasus)'], 
               [zero_cases, non_zero_cases], color=colors, edgecolor='black', linewidth=1.5)
axes[0, 1].set_ylabel('Count', fontsize=11)
axes[0, 1].set_title('Binary Classification Target', fontsize=13, fontweight='bold')
axes[0, 1].grid(axis='y', alpha=0.3)
for i, v in enumerate([zero_cases, non_zero_cases]):
    axes[0, 1].text(i, v + 500, f'{v:,}\n({[pct_zero, pct_non_zero][i]:.1f}%)', 
                    ha='center', fontweight='bold', fontsize=10)

# Distribution of cases > 0
df_cases = df[df['jumlah_kejadian'] > 0]['jumlah_kejadian']
axes[1, 0].hist(df_cases, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
axes[1, 0].set_xlabel('Jumlah Kasus', fontsize=11)
axes[1, 0].set_ylabel('Frequency', fontsize=11)
axes[1, 0].set_title('Distribution of Cases (Only >0)', fontsize=13, fontweight='bold')
axes[1, 0].axvline(df_cases.median(), color='red', linestyle='--', 
                   linewidth=2, label=f'Median: {df_cases.median():.0f}')
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)

# Box plot
axes[1, 1].boxplot(df_cases, vert=True)
axes[1, 1].set_ylabel('Jumlah Kasus', fontsize=11)
axes[1, 1].set_title('Boxplot of Cases (Only >0)', fontsize=13, fontweight='bold')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('01_target_distribution_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 01_target_distribution_analysis.png")

# [B] Temporal Analysis
print("\n[Temporal Analysis]")
temporal = df.groupby('tahun')['jumlah_kejadian'].agg(['sum', 'mean', 'count']).reset_index()
temporal['pct_with_cases'] = df.groupby('tahun').apply(
    lambda x: (x['jumlah_kejadian'] > 0).sum() / len(x) * 100
).values

print(temporal)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Temporal Trends Analysis', fontsize=16, fontweight='bold')

# Total cases per year
axes[0, 0].plot(temporal['tahun'], temporal['sum'], marker='o', linewidth=2, markersize=8)
axes[0, 0].set_xlabel('Tahun', fontsize=11)
axes[0, 0].set_ylabel('Total Kasus', fontsize=11)
axes[0, 0].set_title('Total Cases per Year', fontsize=13, fontweight='bold')
axes[0, 0].grid(alpha=0.3)
for i, v in enumerate(temporal['sum']):
    axes[0, 0].text(temporal['tahun'][i], v + 20, str(int(v)), 
                    ha='center', fontweight='bold')

# Average cases per year
axes[0, 1].bar(temporal['tahun'], temporal['mean'], color='coral', edgecolor='black')
axes[0, 1].set_xlabel('Tahun', fontsize=11)
axes[0, 1].set_ylabel('Rata-rata Kasus', fontsize=11)
axes[0, 1].set_title('Average Cases per Year', fontsize=13, fontweight='bold')
axes[0, 1].grid(axis='y', alpha=0.3)

# Percentage with cases
axes[1, 0].plot(temporal['tahun'], temporal['pct_with_cases'], 
                marker='s', linewidth=2, markersize=8, color='green')
axes[1, 0].set_xlabel('Tahun', fontsize=11)
axes[1, 0].set_ylabel('Persentase (%)', fontsize=11)
axes[1, 0].set_title('% Wilayah dengan Kasus per Year', fontsize=13, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# Number of records per year
axes[1, 1].bar(temporal['tahun'], temporal['count'], color='skyblue', edgecolor='black')
axes[1, 1].set_xlabel('Tahun', fontsize=11)
axes[1, 1].set_ylabel('Jumlah Records', fontsize=11)
axes[1, 1].set_title('Data Records per Year', fontsize=13, fontweight='bold')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('02_temporal_trends.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 02_temporal_trends.png")

# [C] Geographic Analysis
print("\n[Geographic Analysis]")
geo_kabupaten = df.groupby('bps_nama_kabupaten_kota').agg({
    'jumlah_kejadian': ['sum', 'mean', 'max'],
    'bps_nama_desa_kelurahan': 'count'
}).round(2)
geo_kabupaten.columns = ['total_kasus', 'rata_kasus', 'max_kasus', 'jumlah_desa']
geo_kabupaten['pct_with_cases'] = df.groupby('bps_nama_kabupaten_kota').apply(
    lambda x: (x['jumlah_kejadian'] > 0).sum() / len(x) * 100
).round(2)
geo_kabupaten = geo_kabupaten.sort_values('total_kasus', ascending=False)

print("\nTop 10 Kabupaten/Kota:")
print(geo_kabupaten.head(10))

# Visualisasi Top 10
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Geographic Hotspot Analysis', fontsize=16, fontweight='bold')

top10 = geo_kabupaten.head(10)
axes[0].barh(range(len(top10)), top10['total_kasus'], color='indianred', edgecolor='black')
axes[0].set_yticks(range(len(top10)))
axes[0].set_yticklabels(top10.index, fontsize=10)
axes[0].set_xlabel('Total Kasus', fontsize=11)
axes[0].set_title('Top 10 Kabupaten - Total Cases', fontsize=13, fontweight='bold')
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3)

axes[1].barh(range(len(top10)), top10['pct_with_cases'], color='mediumseagreen', edgecolor='black')
axes[1].set_yticks(range(len(top10)))
axes[1].set_yticklabels(top10.index, fontsize=10)
axes[1].set_xlabel('% Wilayah dengan Kasus', fontsize=11)
axes[1].set_title('Top 10 Kabupaten - % Areas with Cases', fontsize=13, fontweight='bold')
axes[1].invert_yaxis()
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('03_geographic_hotspots.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 03_geographic_hotspots.png")

# ============================================
# 5. KEY INSIGHTS
# ============================================

print("\n" + "="*70)
print("KEY INSIGHTS & FINDINGS")
print("="*70)

insights = f"""
CRITICAL INSIGHTS:

1. SEVERE CLASS IMBALANCE ⚠️
   - {pct_zero:.2f}% data tidak memiliki kasus (class 0)
   - {pct_non_zero:.2f}% data memiliki kasus (class 1)
   - Imbalance ratio: {zero_cases/non_zero_cases:.1f}:1
   
   IMPLIKASI:
   → Perlu handling khusus untuk imbalanced data
   → Accuracy bukan metrik utama (misleading!)
   → Focus pada Precision, Recall, F1-Score, ROC-AUC
   → Gunakan class_weight='balanced' di Decision Tree

2. GEOGRAPHIC CONCENTRATION
   - Top 3 kabupaten: {', '.join(geo_kabupaten.head(3).index)}
   - Hotspots berkontribusi {geo_kabupaten.head(3)['total_kasus'].sum() / df['jumlah_kejadian'].sum() * 100:.1f}% total kasus
   
   IMPLIKASI:
   → Geographic features penting untuk model
   → Targeted intervention di hotspot areas
   → Spatial patterns perlu diexplore

3. TEMPORAL PATTERNS
   - Tahun dengan kasus tertinggi: {temporal.loc[temporal['sum'].idxmax(), 'tahun']}
   - Trend: {'Meningkat' if temporal.iloc[-1]['sum'] > temporal.iloc[0]['sum'] else 'Menurun'}
   
   IMPLIKASI:
   → Temporal features (tahun, lag) penting
   → Need for continuous monitoring
   → Time-based intervention strategies

4. DATA SPARSITY
   - Median kasus (bila >0): {df_cases.median():.0f}
   - Max kasus: {df['jumlah_kejadian'].max()}
   - Outliers signifikan ada
   
   IMPLIKASI:
   → Decision Tree cocok (robust to outliers)
   → Binary classification lebih stable
   → Feature engineering critical

5. BUSINESS VALUE
   - Early warning system feasible
   - Clear target untuk classification
   - Actionable insights untuk stakeholder
   
   REKOMENDASI:
   → Binary classification: "Berisiko" vs "Tidak Berisiko"
   → Decision Tree dengan class balancing
   → Feature importance untuk policy making
   → Geographic-based intervention planning
"""

print(insights)

# Save summary
summary_file = {
    'Total_Records': len(df),
    'Periode': f"{df['tahun'].min()}-{df['tahun'].max()}",
    'Kabupaten_Count': df['bps_nama_kabupaten_kota'].nunique(),
    'Zero_Cases_Pct': pct_zero,
    'With_Cases_Pct': pct_non_zero,
    'Imbalance_Ratio': f"{zero_cases/non_zero_cases:.1f}:1",
    'Top_Kabupaten': geo_kabupaten.head(3).index.tolist(),
    'Max_Cases': int(df['jumlah_kejadian'].max()),
    'Median_Cases_NonZero': df_cases.median()
}

summary_df = pd.DataFrame([summary_file])
summary_df.to_csv('00_dataset_summary.csv', index=False)

with open('00_business_understanding_summary.txt', 'w', encoding='utf-8') as f:
    f.write("DECISION TREE PROJECT - BUSINESS UNDERSTANDING\n")
    f.write("="*70 + "\n\n")
    f.write(business_context)
    f.write("\n\n")
    f.write(insights)

print("\n✅ Files saved:")
print("   - 00_dataset_summary.csv")
print("   - 00_business_understanding_summary.txt")
print("   - 01_target_distribution_analysis.png")
print("   - 02_temporal_trends.png")
print("   - 03_geographic_hotspots.png")

print("\n" + "="*70)
print("🎉 BUSINESS & DATA UNDERSTANDING COMPLETED!")
print("="*70)
print("\nNext Step: Run 02_data_preparation_classification.py")
