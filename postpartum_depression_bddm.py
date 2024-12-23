# -*- coding: utf-8 -*-
"""PostPartum Depression-BDDM

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zcF1xa6ORApzcL2Ek-P4awTLsP8wW-ti

1. Ramadhani Reza Saeputra (22.11.5266)
2. Firza Findia Jiven (22.11.5276)
3. Mohammad Fa'iq Ruliff Mustafa (22.11.5297)

##**Klasifikasi Menggunakan Algoritma XGBoost**
"""

!pip install scikit-learn==1.5.2

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, KFold

#XGBoost
import xgboost as xgb
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline

#RandomForest
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.pipeline import Pipeline
import seaborn as sns
import matplotlib.pyplot as plt

from imblearn.over_sampling import SMOTE  # SMOTE for oversampling

df = pd.read_csv("/content/drive/MyDrive/post_natal_data.csv")

df.head(10)

"""####**Pre-Processing Data**"""

df.info()

df.columns

df.drop('Timestamp', axis=1, inplace=True)

df.columns

len(df)

df.describe()

#missing data
total = df.isnull().sum().sort_values(ascending=False)
percent = (df.isnull().sum()/df.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
missing_data.head(20)
print(missing_data)

df = df.dropna() #dihapus karna tidak melebihi 2% data yang kosong

df.isnull().sum()

len(df)

"""####**Encoding Data**"""

from sklearn.preprocessing import LabelEncoder

columns_to_encode = [
    'Feeling sad or Tearful',
    'Irritable towards baby & partner',
    'Trouble sleeping at night',
    'Problems concentrating or making decision',
    'Overeating or loss of appetite',
    'Feeling anxious',
    'Feeling of guilt',
    'Problems of bonding with baby',
    'Suicide attempt'
]

label_encoders = {}
data = df.copy()

for column in columns_to_encode:
    le = LabelEncoder()
    data[column] = le.fit_transform(data[column])
    label_encoders[column] = le

data.head(5)

description = {}

for column in columns_to_encode:
    label_counts = data[column].value_counts().sort_index().to_dict()
    label_mapping = {index: label for index, label in enumerate(label_encoders[column].classes_)}
    description[column] = {"Label Mapping": label_mapping, "Counts": label_counts}

description

age_mapping = {'25-30': 0,
               '30-35': 1,
               '35-40': 2,
               '40-45': 3,
               '45-50': 4
               }

# Daripada memetakan secara langsung dan berpotensi memperkenalkan NaN,
# isi NaN dengan placeholder, misalnya, 0, jika ada setelah pemetaan
data['Age'] = data['Age'].map(age_mapping).fillna(0)

# Pastikan X tidak mengandung nilai NaN apa pun sebelum menerapkan SMOTE
X = data.drop(columns=['Feeling anxious']).fillna(0).values  # Replace NaNs with 0

data.head()

"""####**Exploratory Data**"""

data.describe()

cols = data.columns

for col in cols:
    counts = data[col].value_counts()
    percentages = data[col].value_counts(normalize=True) * 100

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    # Bar chart
    bars = axs[0].bar(counts.index, counts.values, color='skyblue')
    axs[0].set_title(f'{col} Count (Bar Chart)')
    axs[0].set_xlabel('Value')
    axs[0].set_ylabel('Count')
    axs[0].tick_params(axis='x', rotation=45)

    for bar in bars:
        height = bar.get_height()
        axs[0].annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Pie chart
    wedges, texts, autotexts = axs[1].pie(counts, labels=counts.index.map(str), autopct='%1.1f%%')
    axs[1].set_title(f'{col} Count (Pie Chart)')

    plt.setp(autotexts, size=10, weight="bold")

    plt.tight_layout()
    plt.show()
    print()

# Pairplot untuk memvisualisasikan hubungan antara beberapa fitur
sns.pairplot(data, vars=['Age', 'Feeling sad or Tearful', 'Irritable towards baby & partner', 'Trouble sleeping at night'], hue='Feeling anxious')  # Example features, adjust as needed
plt.show()

# Hitung matriks korelasi
correlation_matrix = data.corr()

# Tetapkan ambang batas untuk korelasi yang kuat (misalnya, 0,7 atau lebih tinggi)
threshold = 0.7

# Temukan fitur yang sangat berkorelasi
highly_correlated_features = set()
for i in range(len(correlation_matrix.columns)):
    for j in range(i):
        if abs(correlation_matrix.iloc[i, j]) > threshold:
            colname = correlation_matrix.columns[i]
            highly_correlated_features.add(colname)

# Cetak fitur yang sangat berkorelasi
print("Highly correlated features:")

# Visualisasi matriks korelasi (opsional)
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix Heatmap')
plt.show()

"""###**Balancing Dataset Smote**"""

# Hitung jumlah data 0 dan 1
counts = data['Feeling anxious'].value_counts()

# Tampilkan hasilnya
print("Jumlah data 0 (Tidak Cemas):", counts[0])
print("Jumlah data 1 (Cemas):", counts[1])

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
import pandas as pd

X = data.drop('Feeling anxious', axis=1)
y = data['Feeling anxious']

# Membagi data menjadi data latih dan data uji (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Menampilkan distribusi sebelum oversampling
print("Distribusi data sebelum SMOTE:")
print(y_train.value_counts())

# Inisialisasi SMOTE untuk oversampling
smote = SMOTE(random_state=42)

# Terapkan SMOTE untuk menghasilkan data latih yang seimbang
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Menampilkan distribusi setelah oversampling
print("\nDistribusi data setelah SMOTE:")
print(y_train_resampled.value_counts())

# Optional: Visualisasi distribusi kelas sebelum dan sesudah SMOTE (bila perlu)
import matplotlib.pyplot as plt

# Visualisasi distribusi kelas sebelum dan sesudah SMOTE
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
y_train.value_counts().plot(kind='bar', color='skyblue')
plt.title("Distribusi Kelas Sebelum SMOTE")
plt.xlabel('Kelas')
plt.ylabel('Jumlah')

plt.subplot(1, 2, 2)
y_train_resampled.value_counts().plot(kind='bar', color='salmon')
plt.title("Distribusi Kelas Setelah SMOTE")
plt.xlabel('Kelas')
plt.ylabel('Jumlah')

plt.tight_layout()
plt.show()

"""Spliting Data"""

from sklearn.model_selection import train_test_split

# Setelah SMOTE, data latih telah di-oversample dan menjadi seimbang
# Kita dapat langsung membagi kembali data menjadi data latih dan data uji

# Split data latih dan uji dengan rasio 80% latih, 20% uji
X_train_final, X_test_final, y_train_final, y_test_final = train_test_split(X_train_resampled, y_train_resampled, test_size=0.2, random_state=42)

# Menampilkan bentuk data setelah split
print(f"Dimensi X_train_final: {len(X_train_final)}")
print(f"Dimensi X_test_final: {len(X_test_final)}")
print(f"Distribusi kelas pada data latih setelah SMOTE:\n{y_train_final.value_counts()}")
print(f"Distribusi kelas pada data uji:\n{y_test_final.value_counts()}")

"""###**Klasifikasi dan Evaluasi, XGBoost**

Mencari parameter terbaik untuk pelatihan model
"""

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
import xgboost as xgb

# Menggunakan data yang sudah di-resample dengan SMOTE (X_train_final, y_train_final)
# dan data uji (X_test_final, y_test_final)

# Tentukan parameter grid untuk pencarian terbaik
param_grid = {
    'eta': [0.1, 0.2, 0.3, 0.4, 0.5],  # Learning rate
    'max_depth': [3, 5, 7],   # Depth pohon keputusan
    'n_estimators': [50, 100, 150],  # Jumlah pohon
    'subsample': [0.7, 0.8, 1.0],  # Proporsi data untuk setiap pohon
    'colsample_bytree': [0.7, 0.8, 1.0],  # Proporsi fitur untuk setiap pohon
    'gamma': [0, 0.1, 0.2]  # Regularisasi untuk mencegah overfitting
}

# Inisialisasi model XGBoost
model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', random_state=42)

# Menggunakan GridSearchCV untuk mencari kombinasi parameter terbaik
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)

# Melakukan fitting untuk mencari parameter terbaik
grid_search.fit(X_train_final, y_train_final)

# Menampilkan parameter terbaik dan skor terbaik
print(f"Best parameters found: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_}")

# Menggunakan parameter terbaik untuk membuat model akhir
best_model = grid_search.best_estimator_

# Evaluasi pada data uji
y_pred = best_model.predict(X_test_final)
accuracy = accuracy_score(y_test_final, y_pred)
print(f"Accuracy on test data: {accuracy:.4f}")

from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Recalculate y_pred using the best_model and X_test_final
y_pred = best_model.predict(X_test_final)  # This line is crucial

# Menghitung confusion matrix
cm = confusion_matrix(y_test_final, y_pred)

# Menampilkan confusion matrix dengan visualisasi
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=best_model.classes_)
disp.plot(cmap=plt.cm.Greens)
plt.title("Confusion Matrix")
plt.show()

# Menampilkan laporan klasifikasi
report = classification_report(y_test_final, y_pred, target_names=['Class 0 (Not Anxious)', 'Class 1 (Anxious)'])
print("Classification Report:")
print(report)

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

# Tentukan jumlah percobaan
num_trials = 10

# List untuk menyimpan hasil evaluasi dari setiap percobaan
accuracy_scores = []
precision_scores = []
recall_scores = []
f1_scores = []
roc_auc_scores = []
confusion_matrices = []

# SMOTE untuk menangani data yang tidak seimbang
smote = SMOTE(random_state=42)

# Loop sebanyak num_trials
for trial in range(num_trials):
    print(f"Trial {trial + 1}/{num_trials}")

    # Split data menjadi train dan test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=trial)

    # Oversampling menggunakan SMOTE pada data latih
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    # Inisialisasi model XGBoost dengan parameter terbaik (dari hasil tuning sebelumnya)
    best_params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'eta': 0.2,
        'max_depth': 5,
        'n_estimators': 100,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'gamma': 0.1,
        'random_state': trial
    }
    model = xgb.XGBClassifier(**best_params)

    # Train model
    model.fit(X_train_resampled, y_train_resampled)

    # Predict pada data uji
    y_pred = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)[:, 1]

    # Evaluasi model
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_prob)

    # Simpan hasil evaluasi
    accuracy_scores.append(accuracy)
    precision_scores.append(precision)
    recall_scores.append(recall)
    f1_scores.append(f1)
    roc_auc_scores.append(roc_auc)

    # Simpan confusion matrix
    confusion_matrices.append(confusion_matrix(y_test, y_pred))

    print(f"Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}, ROC-AUC: {roc_auc:.4f}\n")

# Menentukan trial dengan F1-Score terbaik
best_trial_index = np.argmax(f1_scores)
best_confusion_matrix = confusion_matrices[best_trial_index]

# Menampilkan hasil rata-rata dan standar deviasi dari semua percobaan
print("\nSummary of all trials:")
print(f"Average Accuracy: {np.mean(accuracy_scores):.4f} ± {np.std(accuracy_scores):.4f}")
print(f"Average Precision: {np.mean(precision_scores):.4f} ± {np.std(precision_scores):.4f}")
print(f"Average Recall: {np.mean(recall_scores):.4f} ± {np.std(recall_scores):.4f}")
print(f"Average F1-Score: {np.mean(f1_scores):.4f} ± {np.std(f1_scores):.4f}")
print(f"Average ROC-AUC: {np.mean(roc_auc_scores):.4f} ± {np.std(roc_auc_scores):.4f}")

# Menampilkan confusion matrix dari trial terbaik
print(f"\nBest trial index (based on F1-Score): {best_trial_index + 1}")
print("Confusion Matrix:")
print(best_confusion_matrix)

# Visualisasi confusion matrix terbaik
plt.figure(figsize=(8, 6))
sns.heatmap(best_confusion_matrix, annot=True, fmt='d', cmap='Greens',
            xticklabels=['Predicted 0', 'Predicted 1'],
            yticklabels=['Actual 0', 'Actual 1'])
plt.title(f'Confusion Matrix for Best Trial (Trial {best_trial_index + 1})')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()