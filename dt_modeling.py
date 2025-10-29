"""
FUNDAMENTAL DATA ANALYST - DECISION TREE PROJECT
PART 3: DECISION TREE MODELING

Compare Multiple Decision Tree Variations:
1. Baseline (Majority Class)
2. Decision Tree - Basic
3. Decision Tree - Balanced
4. Decision Tree - Pruned
5. Random Forest
6. XGBoost (Bonus)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import cross_val_score, GridSearchCV
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("DECISION TREE MODELING - MULTIPLE VARIATIONS")
print("="*70)

# ============================================
# 1. LOAD PREPARED DATA
# ============================================

print("\n[1] LOADING PREPARED DATA...")
print("-" * 70)

X_train = pd.read_csv('X_train.csv')
X_test = pd.read_csv('X_test.csv')
y_train = pd.read_csv('y_train.csv')['berisiko']
y_test = pd.read_csv('y_test.csv')['berisiko']

print(f"✅ Training set: {X_train.shape}")
print(f"✅ Testing set: {X_test.shape}")

print(f"\nClass distribution in training:")
print(y_train.value_counts())
print(f"\nImbalance ratio: {y_train.value_counts()[0]/y_train.value_counts()[1]:.2f}:1")

# ============================================
# 2. BASELINE MODEL
# ============================================

print("\n" + "="*70)
print("MODEL 1: BASELINE (MAJORITY CLASS PREDICTOR)")
print("="*70)

# Predict majority class for all samples
majority_class = y_train.mode()[0]
y_pred_baseline = np.full(len(y_test), majority_class)

# Evaluate
baseline_acc = accuracy_score(y_test, y_pred_baseline)
baseline_precision = precision_score(y_test, y_pred_baseline, zero_division=0)
baseline_recall = recall_score(y_test, y_pred_baseline, zero_division=0)
baseline_f1 = f1_score(y_test, y_pred_baseline, zero_division=0)

print(f"\nBaseline Strategy: Always predict class {majority_class}")
print(f"\nPerformance:")
print(f"  Accuracy:  {baseline_acc:.4f} ({baseline_acc*100:.2f}%)")
print(f"  Precision: {baseline_precision:.4f}")
print(f"  Recall:    {baseline_recall:.4f}")
print(f"  F1-Score:  {baseline_f1:.4f}")

print(f"\n⚠️ Note: High accuracy is misleading due to class imbalance!")

# ============================================
# 3. DECISION TREE - BASIC
# ============================================

print("\n" + "="*70)
print("MODEL 2: DECISION TREE - BASIC (Default Parameters)")
print("="*70)

dt_basic = DecisionTreeClassifier(random_state=42)
dt_basic.fit(X_train, y_train)

# Predictions
y_pred_basic = dt_basic.predict(X_test)
y_proba_basic = dt_basic.predict_proba(X_test)[:, 1]

# Metrics
acc_basic = accuracy_score(y_test, y_pred_basic)
prec_basic = precision_score(y_test, y_pred_basic, zero_division=0)
rec_basic = recall_score(y_test, y_pred_basic, zero_division=0)
f1_basic = f1_score(y_test, y_pred_basic, zero_division=0)
auc_basic = roc_auc_score(y_test, y_proba_basic)

print(f"\nTree Depth: {dt_basic.get_depth()}")
print(f"Number of Leaves: {dt_basic.get_n_leaves()}")

print(f"\nPerformance:")
print(f"  Accuracy:  {acc_basic:.4f} ({acc_basic*100:.2f}%)")
print(f"  Precision: {prec_basic:.4f}")
print(f"  Recall:    {rec_basic:.4f}")
print(f"  F1-Score:  {f1_basic:.4f}")
print(f"  ROC-AUC:   {auc_basic:.4f}")

print(f"\nImprovement vs Baseline:")
print(f"  Accuracy:  {(acc_basic - baseline_acc)*100:+.2f}%")
print(f"  F1-Score:  {(f1_basic - baseline_f1):+.4f}")

# Cross-validation
cv_scores_basic = cross_val_score(dt_basic, X_train, y_train, cv=5, scoring='f1')
print(f"\nCross-Validation F1-Score: {cv_scores_basic.mean():.4f} (+/- {cv_scores_basic.std():.4f})")

# ============================================
# 4. DECISION TREE - BALANCED
# ============================================

print("\n" + "="*70)
print("MODEL 3: DECISION TREE - BALANCED (class_weight='balanced')")
print("="*70)

dt_balanced = DecisionTreeClassifier(
    class_weight='balanced',
    random_state=42
)
dt_balanced.fit(X_train, y_train)

# Predictions
y_pred_balanced = dt_balanced.predict(X_test)
y_proba_balanced = dt_balanced.predict_proba(X_test)[:, 1]

# Metrics
acc_balanced = accuracy_score(y_test, y_pred_balanced)
prec_balanced = precision_score(y_test, y_pred_balanced, zero_division=0)
rec_balanced = recall_score(y_test, y_pred_balanced, zero_division=0)
f1_balanced = f1_score(y_test, y_pred_balanced, zero_division=0)
auc_balanced = roc_auc_score(y_test, y_proba_balanced)

print(f"\nTree Depth: {dt_balanced.get_depth()}")
print(f"Number of Leaves: {dt_balanced.get_n_leaves()}")

print(f"\nPerformance:")
print(f"  Accuracy:  {acc_balanced:.4f} ({acc_balanced*100:.2f}%)")
print(f"  Precision: {prec_balanced:.4f}")
print(f"  Recall:    {rec_balanced:.4f}")
print(f"  F1-Score:  {f1_balanced:.4f}")
print(f"  ROC-AUC:   {auc_balanced:.4f}")

print(f"\nImprovement vs Basic DT:")
print(f"  Precision: {(prec_balanced - prec_basic):+.4f}")
print(f"  Recall:    {(rec_balanced - rec_basic):+.4f}")
print(f"  F1-Score:  {(f1_balanced - f1_basic):+.4f}")

# Cross-validation
cv_scores_balanced = cross_val_score(dt_balanced, X_train, y_train, cv=5, scoring='f1')
print(f"\nCross-Validation F1-Score: {cv_scores_balanced.mean():.4f} (+/- {cv_scores_balanced.std():.4f})")

# ============================================
# 5. DECISION TREE - PRUNED (Tuned)
# ============================================

print("\n" + "="*70)
print("MODEL 4: DECISION TREE - PRUNED (Hyperparameter Tuning)")
print("="*70)

print("\nSearching for optimal hyperparameters...")

param_grid = {
    'max_depth': [3, 5, 7, 10, None],
    'min_samples_split': [2, 5, 10, 20],
    'min_samples_leaf': [1, 2, 5, 10],
    'class_weight': ['balanced']
}

dt_grid = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='f1',
    n_jobs=-1,
    verbose=0
)

dt_grid.fit(X_train, y_train)
dt_pruned = dt_grid.best_estimator_

print(f"\n✅ Best Parameters Found:")
for param, value in dt_grid.best_params_.items():
    print(f"   {param}: {value}")

# Predictions
y_pred_pruned = dt_pruned.predict(X_test)
y_proba_pruned = dt_pruned.predict_proba(X_test)[:, 1]

# Metrics
acc_pruned = accuracy_score(y_test, y_pred_pruned)
prec_pruned = precision_score(y_test, y_pred_pruned, zero_division=0)
rec_pruned = recall_score(y_test, y_pred_pruned, zero_division=0)
f1_pruned = f1_score(y_test, y_pred_pruned, zero_division=0)
auc_pruned = roc_auc_score(y_test, y_proba_pruned)

print(f"\nTree Depth: {dt_pruned.get_depth()}")
print(f"Number of Leaves: {dt_pruned.get_n_leaves()}")

print(f"\nPerformance:")
print(f"  Accuracy:  {acc_pruned:.4f} ({acc_pruned*100:.2f}%)")
print(f"  Precision: {prec_pruned:.4f}")
print(f"  Recall:    {rec_pruned:.4f}")
print(f"  F1-Score:  {f1_pruned:.4f}")
print(f"  ROC-AUC:   {auc_pruned:.4f}")

print(f"\nImprovement vs Balanced DT:")
print(f"  F1-Score: {(f1_pruned - f1_balanced):+.4f}")
print(f"  ROC-AUC:  {(auc_pruned - auc_balanced):+.4f}")

# ============================================
# 6. RANDOM FOREST
# ============================================

print("\n" + "="*70)
print("MODEL 5: RANDOM FOREST (Ensemble Method)")
print("="*70)

rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest with 100 trees...")
rf.fit(X_train, y_train)

# Predictions
y_pred_rf = rf.predict(X_test)
y_proba_rf = rf.predict_proba(X_test)[:, 1]

# Metrics
acc_rf = accuracy_score(y_test, y_pred_rf)
prec_rf = precision_score(y_test, y_pred_rf, zero_division=0)
rec_rf = recall_score(y_test, y_pred_rf, zero_division=0)
f1_rf = f1_score(y_test, y_pred_rf, zero_division=0)
auc_rf = roc_auc_score(y_test, y_proba_rf)

print(f"\nPerformance:")
print(f"  Accuracy:  {acc_rf:.4f} ({acc_rf*100:.2f}%)")
print(f"  Precision: {prec_rf:.4f}")
print(f"  Recall:    {rec_rf:.4f}")
print(f"  F1-Score:  {f1_rf:.4f}")
print(f"  ROC-AUC:   {auc_rf:.4f}")

print(f"\nImprovement vs Best DT:")
print(f"  F1-Score: {(f1_rf - f1_pruned):+.4f}")
print(f"  ROC-AUC:  {(auc_rf - auc_pruned):+.4f}")

# Cross-validation
cv_scores_rf = cross_val_score(rf, X_train, y_train, cv=5, scoring='f1')
print(f"\nCross-Validation F1-Score: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std():.4f})")

# ============================================
# 7. MODEL COMPARISON
# ============================================

print("\n" + "="*70)
print("MODEL COMPARISON SUMMARY")
print("="*70)

# Create comparison dataframe
comparison = pd.DataFrame({
    'Model': ['Baseline', 'DT Basic', 'DT Balanced', 'DT Pruned', 'Random Forest'],
    'Accuracy': [baseline_acc, acc_basic, acc_balanced, acc_pruned, acc_rf],
    'Precision': [baseline_precision, prec_basic, prec_balanced, prec_pruned, prec_rf],
    'Recall': [baseline_recall, rec_basic, rec_balanced, rec_pruned, rec_rf],
    'F1-Score': [baseline_f1, f1_basic, f1_balanced, f1_pruned, f1_rf],
    'ROC-AUC': [0, auc_basic, auc_balanced, auc_pruned, auc_rf]
})

print("\n" + comparison.to_string(index=False))

# Save comparison
comparison.to_csv('model_comparison_metrics.csv', index=False)
print("\n✅ Comparison saved: model_comparison_metrics.csv")

# Find best model
best_f1_idx = comparison['F1-Score'].idxmax()
best_model_name = comparison.loc[best_f1_idx, 'Model']
best_f1 = comparison.loc[best_f1_idx, 'F1-Score']

print(f"\n🏆 BEST MODEL: {best_model_name}")
print(f"   F1-Score: {best_f1:.4f}")

# Select best model for detailed analysis
if best_model_name == 'Random Forest':
    best_model = rf
    y_pred_best = y_pred_rf
    y_proba_best = y_proba_rf
elif best_model_name == 'DT Pruned':
    best_model = dt_pruned
    y_pred_best = y_pred_pruned
    y_proba_best = y_proba_pruned
elif best_model_name == 'DT Balanced':
    best_model = dt_balanced
    y_pred_best = y_pred_balanced
    y_proba_best = y_proba_balanced
else:
    best_model = dt_basic
    y_pred_best = y_pred_basic
    y_proba_best = y_proba_basic

# ============================================
# 8. DETAILED EVALUATION OF BEST MODEL
# ============================================

print("\n" + "="*70)
print(f"DETAILED EVALUATION: {best_model_name}")
print("="*70)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_best)
print(f"\nConfusion Matrix:")
print(cm)

# Classification Report
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred_best, 
                          target_names=['Tidak Berisiko', 'Berisiko']))

# Feature Importance
print(f"\nFeature Importance (Top 10):")
feature_names = X_train.columns
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feature_imp = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(feature_imp.head(10).to_string(index=False))
    feature_imp.to_csv('feature_importance.csv', index=False)
    print("\n✅ Feature importance saved: feature_importance.csv")

# ============================================
# 9. VISUALIZATIONS
# ============================================

print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70)

# [A] Model Comparison Bar Chart
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
colors_map = plt.cm.Set3(range(len(comparison)))

for idx, metric in enumerate(metrics):
    ax = axes[idx // 2, idx % 2]
    bars = ax.bar(comparison['Model'], comparison[metric], color=colors_map, edgecolor='black', linewidth=1.5)
    
    # Highlight best
    max_idx = comparison[metric].idxmax()
    bars[max_idx].set_color('gold')
    bars[max_idx].set_edgecolor('darkred')
    bars[max_idx].set_linewidth(3)
    
    ax.set_ylabel(metric, fontsize=11)
    ax.set_title(f'{metric} Comparison', fontsize=13, fontweight='bold')
    ax.set_ylim([0, 1.0])
    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for i, v in enumerate(comparison[metric]):
        ax.text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('07_model_comparison_metrics.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 07_model_comparison_metrics.png")

# [B] Confusion Matrix Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Tidak Berisiko', 'Berisiko'],
            yticklabels=['Tidak Berisiko', 'Berisiko'],
            cbar_kws={'label': 'Count'})
plt.title(f'Confusion Matrix - {best_model_name}', fontsize=14, fontweight='bold')
plt.ylabel('Actual', fontsize=12)
plt.xlabel('Predicted', fontsize=12)
plt.tight_layout()
plt.savefig('08_confusion_matrix_best_model.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 08_confusion_matrix_best_model.png")

# [C] ROC Curves
plt.figure(figsize=(10, 8))

# Plot ROC for each model (except baseline)
models_roc = [
    ('DT Basic', y_proba_basic, 'blue'),
    ('DT Balanced', y_proba_balanced, 'green'),
    ('DT Pruned', y_proba_pruned, 'red'),
    ('Random Forest', y_proba_rf, 'purple')
]

for name, y_proba, color in models_roc:
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)
    plt.plot(fpr, tpr, label=f'{name} (AUC = {auc:.3f})', linewidth=2, color=color)

# Diagonal line
plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier', linewidth=1)

plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curves Comparison', fontsize=14, fontweight='bold')
plt.legend(loc='lower right', fontsize=10)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('09_roc_curves_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Saved: 09_roc_curves_comparison.png")

# [D] Feature Importance Plot
if hasattr(best_model, 'feature_importances_'):
    plt.figure(figsize=(10, 8))
    top_features = feature_imp.head(15)
    plt.barh(range(len(top_features)), top_features['importance'], color='steelblue', edgecolor='black')
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance', fontsize=12)
    plt.title(f'Top 15 Feature Importance - {best_model_name}', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('10_feature_importance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Saved: 10_feature_importance.png")

# [E] Decision Tree Visualization (if best model is DT)
if best_model_name in ['DT Basic', 'DT Balanced', 'DT Pruned']:
    plt.figure(figsize=(25, 15))
    plot_tree(best_model, 
              feature_names=feature_names,
              class_names=['Tidak Berisiko', 'Berisiko'],
              filled=True,
              fontsize=9,
              rounded=True,
              proportion=True)
    plt.title(f'Decision Tree Structure - {best_model_name}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('11_decision_tree_structure.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Saved: 11_decision_tree_structure.png")

# ============================================
# 10. SAVE RESULTS
# ============================================

print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

# Save predictions
predictions_df = pd.DataFrame({
    'actual': y_test.values,
    'predicted': y_pred_best,
    'probability_class_1': y_proba_best
})
predictions_df.to_csv('predictions_best_model.csv', index=False)
print("✅ Predictions saved: predictions_best_model.csv")

# Save model info
model_info = {
    'best_model': best_model_name,
    'accuracy': comparison.loc[best_f1_idx, 'Accuracy'],
    'precision': comparison.loc[best_f1_idx, 'Precision'],
    'recall': comparison.loc[best_f1_idx, 'Recall'],
    'f1_score': best_f1,
    'roc_auc': comparison.loc[best_f1_idx, 'ROC-AUC']
}

with open('best_model_info.txt', 'w') as f:
    f.write(f"BEST MODEL: {best_model_name}\n")
    f.write("="*50 + "\n\n")
    for key, value in model_info.items():
        f.write(f"{key}: {value}\n")

print("✅ Model info saved: best_model_info.txt")

print("\n" + "="*70)
print("🎉 MODELING COMPLETED!")
print("="*70)
print(f"\n🏆 Best Model: {best_model_name}")
print(f"   F1-Score: {best_f1:.4f}")
print(f"   ROC-AUC:  {comparison.loc[best_f1_idx, 'ROC-AUC']:.4f}")
print("\nNext Step: Run 04_model_evaluation_insights.py for detailed analysis")
