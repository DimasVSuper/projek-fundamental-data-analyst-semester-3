"""
FUNDAMENTAL DATA ANALYST - DECISION TREE PROJECT
PART 2: DATA PREPARATION FOR CLASSIFICATION

Focus: Feature Engineering untuk Binary Classification
Target: Wilayah "Berisiko" (>0 kasus) vs "Tidak Berisiko" (0 kasus)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("DATA PREPARATION FOR DECISION TREE CLASSIFICATION")
print("="*70)

# ============================================
# 1. LOAD DATA
# ============================================

print("\n[1] LOADING DATA...")
print("-" * 70)

df = pd.read_csv('jml_kejadian_bunuh_diri__des_kel.csv')
print(f"✅ Dataset loaded: {len(df):,} records")

# ============================================
# 2. FEATURE ENGINEERING
# ============================================

print("\n" + "="*70)
print("FEATURE ENGINEERING")
print("="*70)

# [A] AGREGASI PER KABUPATEN & TAHUN
print("\n[A] Agregating data per Kabupaten & Tahun...")

df_agg = df.groupby(['bps_nama_kabupaten_kota', 'tahun']).agg({
    'jumlah_kejadian': ['sum', 'mean', 'max', 'std', 'count'],
    'bps_nama_kecamatan': 'nunique',
    'bps_nama_desa_kelurahan': 'nunique'
}).reset_index()

# Flatten column names
df_agg.columns = ['kabupaten', 'tahun', 'total_kasus', 'rata_kasus', 
                  'max_kasus', 'std_kasus', 'count_records',
                  'jumlah_kecamatan', 'jumlah_desa']

# Handle NaN in std
df_agg['std_kasus'].fillna(0, inplace=True)

print(f"✅ Aggregated shape: {df_agg.shape}")
print(f"   Features: {list(df_agg.columns)}")

# [B] TEMPORAL FEATURES (LAG & TREND)
print("\n[B] Creating temporal features...")

df_agg = df_agg.sort_values(['kabupaten', 'tahun']).reset_index(drop=True)

# Lag features
df_agg['kasus_1tahun_lalu'] = df_agg.groupby('kabupaten')['total_kasus'].shift(1)
df_agg['kasus_2tahun_lalu'] = df_agg.groupby('kabupaten')['total_kasus'].shift(2)

# Trend
df_agg['tren'] = df_agg['total_kasus'] - df_agg['kasus_1tahun_lalu']

# Growth rate (handle division by zero)
df_agg['growth_rate'] = df_agg.apply(
    lambda row: ((row['total_kasus'] - row['kasus_1tahun_lalu']) / row['kasus_1tahun_lalu'] * 100) 
    if pd.notna(row['kasus_1tahun_lalu']) and row['kasus_1tahun_lalu'] > 0 
    else 0, 
    axis=1
)

# Rolling statistics (2 years window)
df_agg['rolling_mean_2y'] = df_agg.groupby('kabupaten')['total_kasus'].transform(
    lambda x: x.rolling(window=2, min_periods=1).mean()
)

df_agg['rolling_max_2y'] = df_agg.groupby('kabupaten')['total_kasus'].transform(
    lambda x: x.rolling(window=2, min_periods=1).max()
)

print("✅ Temporal features created:")
print("   - kasus_1tahun_lalu, kasus_2tahun_lalu")
print("   - tren, growth_rate")
print("   - rolling_mean_2y, rolling_max_2y")

# [C] GEOGRAPHIC FEATURES
print("\n[C] Creating geographic features...")

# Total historis per kabupaten (all years)
total_historis = df.groupby('bps_nama_kabupaten_kota')['jumlah_kejadian'].sum()
df_agg['total_kasus_historis'] = df_agg['kabupaten'].map(total_historis)

# Rata-rata kasus per desa
df_agg['kasus_per_desa'] = df_agg['total_kasus'] / df_agg['jumlah_desa']

# Density score (kasus per kecamatan)
df_agg['density_score'] = df_agg['total_kasus'] / df_agg['jumlah_kecamatan']

# Severity indicator (max relative to mean)
df_agg['severity_ratio'] = df_agg.apply(
    lambda row: row['max_kasus'] / row['rata_kasus'] if row['rata_kasus'] > 0 else 0,
    axis=1
)

print("✅ Geographic features created:")
print("   - total_kasus_historis")
print("   - kasus_per_desa")
print("   - density_score")
print("   - severity_ratio")

# [D] CATEGORICAL ENCODING
print("\n[D] Encoding categorical features...")

le = LabelEncoder()
df_agg['kabupaten_encoded'] = le.fit_transform(df_agg['kabupaten'])

# Save label encoder mapping
kabupaten_mapping = pd.DataFrame({
    'kabupaten': le.classes_,
    'encoded_value': range(len(le.classes_))
})
kabupaten_mapping.to_csv('kabupaten_encoding_mapping.csv', index=False)

print(f"✅ Encoded {len(le.classes_)} kabupaten")
print("   Mapping saved to: kabupaten_encoding_mapping.csv")

# [E] CREATE BINARY TARGET
print("\n[E] Creating binary target variable...")

df_agg['berisiko'] = (df_agg['total_kasus'] > 0).astype(int)

target_dist = df_agg['berisiko'].value_counts()
print(f"\n✅ Binary target created:")
print(f"   Class 0 (Tidak Berisiko): {target_dist[0]} ({target_dist[0]/len(df_agg)*100:.2f}%)")
print(f"   Class 1 (Berisiko):       {target_dist[1]} ({target_dist[1]/len(df_agg)*100:.2f}%)")
print(f"   Imbalance ratio: {target_dist[0]/target_dist[1]:.2f}:1")

# ============================================
# 3. HANDLE MISSING VALUES
# ============================================

print("\n" + "="*70)
print("HANDLING MISSING VALUES")
print("="*70)

print("\nMissing values BEFORE handling:")
missing_before = df_agg.isnull().sum()
print(missing_before[missing_before > 0])

# Fill NaN in lag features with 0
fill_cols = ['kasus_1tahun_lalu', 'kasus_2tahun_lalu', 'tren', 'growth_rate']
for col in fill_cols:
    df_agg[col].fillna(0, inplace=True)

print("\nMissing values AFTER handling:")
missing_after = df_agg.isnull().sum()
if missing_after.sum() == 0:
    print("✅ No missing values!")
else:
    print(missing_after[missing_after > 0])

# ============================================
# 4. FEATURE SELECTION
# ============================================

print("\n" + "="*70)
print("FEATURE SELECTION")
print("="*70)

# Select features untuk modeling
feature_cols = [
    # Temporal
    'tahun',
    'kasus_1tahun_lalu',
    'kasus_2tahun_lalu',
    'tren',
    'growth_rate',
    'rolling_mean_2y',
    'rolling_max_2y',
    
    # Geographic
    'kabupaten_encoded',
    'jumlah_kecamatan',
    'jumlah_desa',
    'kasus_per_desa',
    'density_score',
    'total_kasus_historis',
    
    # Statistical
    'rata_kasus',
    'max_kasus',
    'std_kasus',
    'severity_ratio',
    'count_records'
]

print(f"\n✅ Selected {len(feature_cols)} features:")
for i, feat in enumerate(feature_cols, 1):
    print(f"   {i:2d}. {feat}")

# ============================================
# 5. DATA SPLITTING
# ============================================

print("\n" + "="*70)
print("TRAIN-TEST SPLIT")
print("="*70)

# Remove rows with any remaining NaN
df_clean = df_agg.dropna()
print(f"\nData after dropna: {len(df_clean)} records")

# Prepare X and y
X = df_clean[feature_cols]
y = df_clean['berisiko']

print(f"\nFeature matrix shape: {X.shape}")
print(f"Target vector shape: {y.shape}")

# Stratified split (maintain class distribution)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

print(f"\n✅ Data split completed:")
print(f"   Training set:   {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"   Testing set:    {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")

print(f"\n   Class distribution in TRAINING set:")
train_dist = y_train.value_counts()
print(f"      Class 0: {train_dist[0]} ({train_dist[0]/len(y_train)*100:.2f}%)")
print(f"      Class 1: {train_dist[1]} ({train_dist[1]/len(y_train)*100:.2f}%)")

print(f"\n   Class distribution in TESTING set:")
test_dist = y_test.value_counts()
print(f"      Class 0: {test_dist[0]} ({test_dist[0]/len(y_test)*100:.2f}%)")
print(f"      Class 1: {test_dist[1]} ({test_dist[1]/len(y_test)*100:.2f}%)")

# ============================================
# 6. SAVE PREPARED DATA
# ============================================

print("\n" + "="*70)
print("SAVING PREPARED DATA")
print("="*70)

# Save train-test splits
X_train.to_csv('X_train.csv', index=False)
X_test.to_csv('X_test.csv', index=False)
y_train.to_csv('y_train.csv', index=False, header=['berisiko'])
y_test.to_csv('y_test.csv', index=False, header=['berisiko'])

print("✅ Train-test data saved:")
print("   - X_train.csv")
print("   - X_test.csv")
print("   - y_train.csv")
print("   - y_test.csv")

# Save complete processed dataset (for reference)
df_clean.to_csv('data_processed_complete.csv', index=False)
print("   - data_processed_complete.csv")

# Save feature list
feature_list_df = pd.DataFrame({
    'feature_name': feature_cols,
    'feature_index': range(len(feature_cols))
})
feature_list_df.to_csv('feature_list.csv', index=False)
print("   - feature_list.csv")

# ============================================
# 7. EXPLORATORY VISUALIZATION
# ============================================

print("\n" + "="*70)
print("CREATING EXPLORATORY VISUALIZATIONS")
print("="*70)

# [A] Feature distributions by class
print("\n[A] Feature distributions...")

# Select numeric features for visualization
viz_features = ['total_kasus', 'kasus_1tahun_lalu', 'tren', 'growth_rate',
                'kasus_per_desa', 'density_score', 'jumlah_desa']

fig, axes = plt.subplots(3, 3, figsize=(16, 12))
fig.suptitle('Feature Distributions by Class', fontsize=16, fontweight='bold')
axes = axes.ravel()

for idx, feat in enumerate(viz_features):
    if idx < len(axes):
        df_clean.boxplot(column=feat, by='berisiko', ax=axes[idx])
        axes[idx].set_title(f'{feat}')
        axes[idx].set_xlabel('Berisiko (0=Tidak, 1=Ya)')
        axes[idx].get_figure().suptitle('')  # Remove auto title

# Hide unused subplots
for idx in range(len(viz_features), len(axes)):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('04_feature_distributions_by_class.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 04_feature_distributions_by_class.png")

# [B] Correlation matrix
print("\n[B] Correlation analysis...")

# Select key numeric features
corr_features = ['total_kasus', 'kasus_1tahun_lalu', 'kasus_2tahun_lalu', 
                 'tren', 'jumlah_desa', 'kasus_per_desa', 'density_score',
                 'total_kasus_historis', 'rolling_mean_2y', 'berisiko']

corr_matrix = df_clean[corr_features].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
            center=0, square=True, linewidths=1,
            cbar_kws={'label': 'Correlation Coefficient'})
plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('05_correlation_matrix.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 05_correlation_matrix.png")

# [C] Class balance visualization
print("\n[C] Class balance comparison...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Class Distribution: Train vs Test', fontsize=16, fontweight='bold')

# Training set
train_counts = y_train.value_counts()
axes[0].bar(['Tidak Berisiko\n(Class 0)', 'Berisiko\n(Class 1)'], 
            train_counts.values, color=['lightcoral', 'lightgreen'],
            edgecolor='black', linewidth=2)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].set_title('Training Set', fontsize=13, fontweight='bold')
axes[0].grid(axis='y', alpha=0.3)
for i, v in enumerate(train_counts.values):
    pct = v / len(y_train) * 100
    axes[0].text(i, v + 2, f'{v}\n({pct:.1f}%)', ha='center', fontweight='bold')

# Testing set
test_counts = y_test.value_counts()
axes[1].bar(['Tidak Berisiko\n(Class 0)', 'Berisiko\n(Class 1)'], 
            test_counts.values, color=['lightcoral', 'lightgreen'],
            edgecolor='black', linewidth=2)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].set_title('Testing Set', fontsize=13, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(test_counts.values):
    pct = v / len(y_test) * 100
    axes[1].text(i, v + 1, f'{v}\n({pct:.1f}%)', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('06_train_test_class_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 06_train_test_class_distribution.png")

# ============================================
# 8. SUMMARY REPORT
# ============================================

print("\n" + "="*70)
print("DATA PREPARATION SUMMARY")
print("="*70)

summary = f"""
DATA PREPARATION SUMMARY
{'='*70}

ORIGINAL DATA:
- Total records: {len(df):,}
- After aggregation: {len(df_agg):,}
- After cleaning: {len(df_clean):,}

FEATURE ENGINEERING:
✅ {len(feature_cols)} features created:
   - 7 Temporal features (lag, trend, rolling stats)
   - 6 Geographic features (density, per-desa metrics)
   - 4 Statistical features (mean, max, std, severity)

TARGET VARIABLE:
- Binary classification: Berisiko (1) vs Tidak Berisiko (0)
- Class 0: {target_dist[0]} samples ({target_dist[0]/len(df_clean)*100:.2f}%)
- Class 1: {target_dist[1]} samples ({target_dist[1]/len(df_clean)*100:.2f}%)
- Imbalance ratio: {target_dist[0]/target_dist[1]:.2f}:1

DATA SPLIT:
- Training: {len(X_train)} samples (80%)
  • Class 0: {train_dist[0]} ({train_dist[0]/len(y_train)*100:.2f}%)
  • Class 1: {train_dist[1]} ({train_dist[1]/len(y_train)*100:.2f}%)
  
- Testing: {len(X_test)} samples (20%)
  • Class 0: {test_dist[0]} ({test_dist[0]/len(y_test)*100:.2f}%)
  • Class 1: {test_dist[1]} ({test_dist[1]/len(y_test)*100:.2f}%)

HANDLING IMBALANCE:
Strategy for Decision Tree modeling:
1. Use class_weight='balanced'
2. Stratified sampling (done)
3. Focus on Precision, Recall, F1-Score (not just Accuracy)
4. Use ROC-AUC for overall performance

KEY FEATURES (Expected High Importance):
- kasus_1tahun_lalu (historical indicator)
- total_kasus_historis (geographic risk)
- density_score (population density factor)
- rolling_mean_2y (trend indicator)
- kabupaten_encoded (location)

FILES GENERATED:
✅ X_train.csv, X_test.csv
✅ y_train.csv, y_test.csv
✅ data_processed_complete.csv
✅ feature_list.csv
✅ kabupaten_encoding_mapping.csv
✅ 04_feature_distributions_by_class.png
✅ 05_correlation_matrix.png
✅ 06_train_test_class_distribution.png

READY FOR MODELING:
✅ Data cleaned and preprocessed
✅ Features engineered
✅ Train-test split completed
✅ Class distribution maintained (stratified)
✅ All files saved for reproducibility

NEXT STEP:
Run 03_decision_tree_modeling.py to build and compare multiple Decision Tree models.
"""

print(summary)

# Save summary to file
with open('01_data_preparation_summary.txt', 'w', encoding='utf-8') as f:
    f.write(summary)

print("\n✅ Summary saved: 01_data_preparation_summary.txt")

print("\n" + "="*70)
print("🎉 DATA PREPARATION COMPLETED!")
print("="*70)
print("\nNext Step: Run 03_decision_tree_modeling.py")
