import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, validation_curve
from sklearn import svm, tree
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve, roc_auc_score, classification_report
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
import json
import os

# Read the csv files and create pandas dataframes
legitimate_df = pd.read_csv("structured_data_legitimate.csv")
phishing_df = pd.read_csv("structured_data_phishing.csv")

# Combine legitimate and phishing dataframes, and shuffle
df = pd.concat([legitimate_df, phishing_df], axis=0).sample(frac=1)

# Remove 'URL' column and remove duplicates
df = df.drop('URL', axis=1).drop_duplicates()

# Create X and Y for the models, Supervised Learning
X = df.drop('label', axis=1)
Y = df['label']

# Apply SMOTE to balance the classes
smote = SMOTE(random_state=10)
X_res, Y_res = smote.fit_resample(X, Y)

# Split data into train and test
x_train, x_test, y_train, y_test = train_test_split(X_res, Y_res, test_size=0.2, random_state=10)

# Initialize models
nb_model = GaussianNB()
svm_model = svm.SVC(probability=True)  # Enable probability estimates for SVM
dt_model = tree.DecisionTreeClassifier()
rf_model = RandomForestClassifier(n_estimators=60)

# Function to plot ROC curve
def plot_roc_curve(y_test, y_pred_proba, model_name):
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'Receiver Operating Characteristic - {model_name}')
    plt.legend(loc="lower right")
    
    # Save the ROC curve plot
    plt.savefig(f'roc_curve_{model_name}.png')
    plt.close()

# Function to plot validation curve
def plot_validation_curve(model, title, X, y, param_name, param_range, cv):
    train_scores, test_scores = validation_curve(
        model, X, y, param_name=param_name, param_range=param_range,
        cv=cv, scoring="accuracy", n_jobs=-1
    )
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.title(title)
    plt.xlabel(param_name)
    plt.ylabel("Score")
    plt.ylim(0.0, 1.1)
    lw = 2
    plt.semilogx(param_range, train_scores_mean, label="Training score",
                 color="darkorange", lw=lw)
    plt.fill_between(param_range, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.2,
                     color="darkorange", lw=lw)
    plt.semilogx(param_range, test_scores_mean, label="Cross-validation score",
                 color="navy", lw=lw)
    plt.fill_between(param_range, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.2,
                     color="navy", lw=lw)
    plt.legend(loc="best")
    plt.savefig(f'{title}.png')
    plt.show()

# Train models and store results
results = []
for model, model_name in [(nb_model, "Naive Bayes"), (svm_model, "SVM"), (dt_model, "Decision Tree"), (rf_model, "Random Forest")]:
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    y_pred_proba = model.predict_proba(x_test)[:, 1] if hasattr(model, "predict_proba") else model.decision_function(x_test)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    # Precision-Recall AUC
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    sorted_idx = np.argsort(recall)
    precision = precision[sorted_idx]
    recall = recall[sorted_idx]
    pr_auc = auc(recall, precision)
    
    # Plot ROC curve and save
    plot_roc_curve(y_test, y_pred_proba, model_name)
    
    results.append({
        "Model": model_name,
        "Accuracy": model.score(x_test, y_test),
        "ROC AUC": roc_auc,
        "PR AUC": pr_auc,
        "Confusion Matrix": json.dumps(confusion_matrix(y_test, y_pred).tolist()),  # Convert confusion matrix to JSON string
        "Classification Report": json.dumps(classification_report(y_test, y_pred, output_dict=True))
    })

    # Example usage of validation curve
    if model_name == "Random Forest":
        param_range = np.arange(10, 100, 10)  # Example range for n_estimators
        plot_validation_curve(model, f"Validation Curve - {model_name}", X_res, Y_res, param_name='n_estimators', param_range=param_range, cv=5)

# Create DataFrame for results
results_df = pd.DataFrame(results)
results_df.to_csv('model_results.csv', index=False)

