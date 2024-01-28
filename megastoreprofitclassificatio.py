# -*- coding: utf-8 -*-
"""MegastoreProfitClassificatio.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pqYrCcQJEAUC1XOGDV4Bl2ggt7BK8u8y

## Used Moduleas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msnum                             # Draw diagram shows the distribution of the null values
import json
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder,LabelEncoder   # Perform Lable encoding and one-hot encoding to string values
from sklearn.feature_selection import mutual_info_regression
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso
from tabulate import tabulate
from sklearn.feature_selection import f_regression, SelectKBest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, ConfusionMatrixDisplay
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from scipy.stats import norm
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV

"""#Global Variables"""

models = {}
fs = {}

"""#Testing Script

##Helper Function to save the model
"""

def save_model(model_name):
  """ Save ML model to file """
  global models
  pickle.dump(models[model_name], open(model_name + ".sav", 'wb'))
  pickle.dump(fs[model_name], open(model_name + "_fs" + ".sav", 'wb'))

"""##Helper Function to load the model"""

def load_model(model_name):
  """ Load a ML model from file """
  global models
  models[model_name] = pickle.load(open(model_name + ".sav", 'rb'))
  fs[model_name] = pickle.load(open(model_name + "_fs" + ".sav", 'rb'))

"""##Classification Testing Script"""

def evaluate_classification_model(x_train, y_train, x_test, y_test, model_name):
    model = load_model(model_name)

    # Predict on the training data
    y_train_pred = model.predict(x_train)

    # Predict on the testing data
    y_test_pred = model.predict(x_test)

    # Calculate evaluation metrics for training data
    train_score = model.score(x_train, y_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    train_precision = precision_score(y_train, y_train_pred)
    train_recall = recall_score(y_train, y_train_pred)

    # Calculate evaluation metrics for testing data
    test_score = model.score(x_test, y_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    test_precision = precision_score(y_test, y_test_pred)
    test_recall = recall_score(y_test, y_test_pred)

    # Print evaluation metrics
    score_table = [["Train Score", train_score], ["Test Score", test_score]]
    score_table.append(["Train Accuracy", train_accuracy])
    score_table.append(["Test Accuracy", test_accuracy])
    score_table.append(["Train Precision", train_precision])
    score_table.append(["Test Precision", test_precision])
    score_table.append(["Train Recall", train_recall])
    score_table.append(["Test Recall", test_recall])

    print(tabulate(score_table), "\n")

    # Print classification report
    print("Training Classification Report:")
    print(classification_report(y_train, y_train_pred), "\n")

    print("Testing Classification Report:")
    print(classification_report(y_test, y_test_pred), "\n")

    # Display confusion matrix for testing data
    ConfusionMatrixDisplay.from_estimator(model, x_test, y_test)

"""## Regression Testing Script"""

def test_regression_model(x_train, x_test ,y_train, y_test,model_name)
    model = load_model(model_name)

    # Predict on the training data
    y_train_predicted = model_name.predict(x_train)

    # Evaluate performance on the training data
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_predicted))
    train_mse = mean_squared_error(y_train, y_train_predicted)
    train_r2 = r2_score(y_train, y_train_predicted)

    # Predict on the testing data
    y_test_predicted = model_name.predict(x_test)

    # Evaluate performance on the testing data
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_predicted))
    test_mse = mean_squared_error(y_test, y_test_predicted)
    test_r2 = r2_score(y_test, y_test_predicted)

    # Print performance metrics
    print("Training set performance:")
    print("RMSE:", train_rmse)
    print("MSE:", train_mse)
    print("R-squared:", train_r2)

    print("Testing set performance:")
    print("RMSE:", test_rmse)
    print("MSE:", test_mse)
    print("R-squared:", test_r2)

"""# Test Script to take the new dataset and apply prediction on it"""

def predict_new_data(csv_file, model_name):
    # Load the ML model
    model = load_model(model_name)

    # Read the new CSV file
    new_data = pd.read_csv(csv_file)

    # Preprocess the new data using the saved preprocessing steps in the model
    preprocessed_data = model.transform(new_data)

    # Make predictions on the preprocessed data
    predictions = model.predict(preprocessed_data)

    return predictions

"""#**Dataset Analysis and Cleaning**

##Load Dataset
"""

dataset = pd.read_csv("/content/megastore-classification-dataset.csv")
dataset.head()

"""# Attributes of dataset"""

uniq_table = []

for key in dataset:
  uniq_values = dataset[key].unique()
  uniq_values.sort()
  dtype = (dataset[key].dtype, "string")[dataset[key].dtype == "O"]
  uniq_table.append([key, dtype, len(uniq_values), uniq_values])

print(tabulate(uniq_table, headers=["Attribute", "Data Type", "Unique Values Count", "Unique Values"], tablefmt="pipe"))

"""# Check if the Data contains Null values"""

msnum.matrix(dataset)
dataset.isnull().sum()
# Replace missing values with mean of each column
dataset.fillna(dataset.mean(), inplace=True)

# recheck if the dataset contains any Null values
dataset.isnull().sum()

"""## Remove Duplicates"""

print("Dataset before removing duplicates: ", dataset.shape)
dataset.drop_duplicates(inplace=True)
print("Dataset after removing duplicates: ", dataset.shape)

"""##Convert Date columns to Datetime format"""

# Convert date columns to datetime format
dataset['Order Date'] = pd.to_datetime(dataset['Order Date'], format='%m/%d/%Y')
dataset['Ship Date'] = pd.to_datetime(dataset['Ship Date'], format='%m/%d/%Y')
dataset['Time to Deliver'] = dataset['Order Date'] - dataset['Ship Date']

"""## Features Enginearing

### Extract a new feature " time to deliver "
"""

# Fix JSON formatting in CategoryTree column
dataset['CategoryTree'] = dataset['CategoryTree'].str.replace("'", '"')

# Convert CategoryTree column from JSON string to dictionary
dataset['CategoryTree'] = dataset['CategoryTree'].apply(lambda x: json.loads(x))

# Extract MainCategory and SubCategory columns
dataset[['MainCategory', 'SubCategory']] = dataset['CategoryTree'].apply(lambda x: pd.Series([x['MainCategory'], x['SubCategory']]))

# Drop the original CategoryTree column if desired
dataset.drop('CategoryTree', axis=1, inplace=True)

"""### Extract Main category and sub-category from the category tree column

"""

# Convert 'Order Date' and 'Ship Date' to Unix timestamp
dataset['Order Date'] = (pd.to_datetime(dataset['Order Date']) - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
dataset['Ship Date'] = (pd.to_datetime(dataset['Ship Date']) - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

# Extract day, month, and year values from delivery date
dataset['Time to Deliver Day'] = dataset['Time to Deliver'].dt.days
dataset['Time to Deliver Month'] = dataset['Time to Deliver'].dt.components['days'] // 30
dataset['Time to Deliver Year'] = dataset['Time to Deliver'].dt.components['days'] // 365

# Split date column into day, month, and year columns
dataset['Order Day'] = pd.to_datetime(dataset['Order Date'], unit='s').dt.day
dataset['Order Month'] = pd.to_datetime(dataset['Order Date'], unit='s').dt.month
dataset['Order Year'] = pd.to_datetime(dataset['Order Date'], unit='s').dt.year

# Drop original date column
dataset.drop('Order Date', axis=1, inplace=True)

# Repeat for 'Ship Date' column
dataset['Ship Day'] = pd.to_datetime(dataset['Ship Date'], unit='s').dt.day
dataset['Ship Month'] = pd.to_datetime(dataset['Ship Date'], unit='s').dt.month
dataset['Ship Year'] = pd.to_datetime(dataset['Ship Date'], unit='s').dt.year
dataset.drop('Ship Date', axis=1, inplace=True)

# Drop the 'Delivery Date' column
dataset.drop('Time to Deliver', axis=1, inplace=True)

# Importing LabelEncoder from Sklearn
# library from preprocessing Module.
from sklearn.preprocessing import LabelEncoder

# Creating a instance of label Encoder.
le = LabelEncoder()

# Using .fit_transform function to fit label
# encoder and return encoded label
label = le.fit_transform(dataset['ReturnCategory'])

# printing label
# label
y=label
print(y)


# removing the column 'Purchased' from df
# as it is of no use now.
dataset.drop("ReturnCategory", axis=1, inplace=True)

# Appending the array to our dataFrame
# with column name 'Purchased'
dataset["ReturnCategory"] = label

# printing Dataframe
dataset

# Split the dataset to x and y
x = dataset.drop('ReturnCategory', axis=1)
y = dataset['ReturnCategory']

x.shape
y.shape

#Get the correlation between the features
megastore_data = dataset.iloc[:, :]
corr = megastore_data.corr()

# print the correlation of each column with the target column
for col in corr.columns:
    print(f"{col} - ReturnCategory: {corr.loc[col, 'ReturnCategory']}")

# Drop the target column from the correlation matrix
corr = corr.drop('ReturnCategory')

# sns.heatmap(dataset.corr(),annot = True)
# plt.show()

sns.set(style="white")
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
f, ax = plt.subplots(figsize=(11, 9))
cmap = sns.diverging_palette(220, 10, as_cmap=True)
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})

# # Identify categorical columns
# cat_cols = x.select_dtypes(include=['object']).columns.tolist()

# # Fit label encoder to training and test data
# for col in cat_cols:
#     label_encoder = LabelEncoder()
#     label_encoder.fit(list(x[col].values) + list(x[col].values))
#     x[col] = label_encoder.transform(x[col])
#     # x_test[col] = label_encoder.transform(x_test[col])

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Identify categorical columns
cat_cols = x_train.select_dtypes(include=['object']).columns.tolist()

# Fit label encoder to training and test data
for col in cat_cols:
    label_encoder = LabelEncoder()
    label_encoder.fit(list(x_train[col].values) + list(x_test[col].values))
    x_train[col] = label_encoder.transform(x_train[col])
    x_test[col] = label_encoder.transform(x_test[col])

# Make sure all values' data type are float
x_train = x_train.astype(float)
x_test = x_test.astype(float)

from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import MinMaxScaler

# Visualize boxplots of each feature before scaling.
fig, axs = plt.subplots(1, 4, figsize=(15, 5))
axs[0].boxplot(dataset['Sales'])
axs[0].set_title('Sales')
axs[1].boxplot(dataset['Discount'])
axs[1].set_title('Discount')
axs[2].boxplot(dataset['Quantity'])
axs[2].set_title('Quantity')
axs[3].boxplot(dataset['ReturnCategory'])
axs[3].set_title('ReturnCategory')
plt.show()


# Set the desired significance level (0.05 for a 95% confidence interval).
alpha = 0.05

# Fit the MedianScaler on training data.
scaler = RobustScaler(with_centering=True, with_scaling=False, quantile_range=(25.0, 75.0)).fit(x_train[['Sales']])

# Perform outlier detection and filtering on training data.
train_medians = scaler.transform(x_train[['Sales']])
train_abs_medians = np.abs(train_medians)
train_median_threshold = np.median(train_abs_medians) * norm.ppf(1 - alpha/2)  # Two-tailed test.
train_filtered_entries = (train_abs_medians < train_median_threshold).all(axis=1)
x_train = x_train[train_filtered_entries]
y_train = y_train[train_filtered_entries]

# Perform outlier detection and filtering on testing data.
test_medians = scaler.transform(x_test[['Sales']])
test_abs_medians = np.abs(test_medians)
test_median_threshold = np.median(test_abs_medians) * norm.ppf(1 - alpha/2)  # Two-tailed test.
test_filtered_entries = (test_abs_medians < test_median_threshold).all(axis=1)
x_test = x_test[test_filtered_entries]
y_test = y_test[test_filtered_entries]

#Trying to remove the effect of the outliers on the target variable with min max scaling to scale it from 0 to 1
scaler = MinMaxScaler()

scaler.fit(y_train.values.reshape(-1, 1))

y_train = pd.DataFrame(scaler.transform(y_train.values.reshape(-1, 1)), columns=['ReturnCategory'])
y_test = pd.DataFrame(scaler.transform(y_test.values.reshape(-1, 1)), columns=['ReturnCategory'])

# Visualize boxplots of each feature after scaling.
fig, axs = plt.subplots(1, 4, figsize=(15, 5))
axs[0].boxplot(x_train['Sales'])
axs[0].set_title('Sales')
axs[1].boxplot(x_train['Discount'])
axs[1].set_title('Discount')
axs[2].boxplot(x_train['Quantity'])
axs[2].set_title('Quantity')
axs[3].boxplot(y_train['ReturnCategory'])
axs[3].set_title('ReturnCategory')
plt.show()

# Concatenate the X and y dataframes to get the correlation matrix
train_data = pd.concat([x_train, y_train], axis=1)

# Get the correlation between the features and the target variable
corr = train_data.corr()

# Print the correlation of each feature with the target variable
print("Correlation of each feature with the target variable (ReturnCategory):")
print(corr['ReturnCategory'])

# Drop the target variable from the correlation matrixa
corr = corr.drop('ReturnCategory')

# Create a bar plot of the correlations
target_column = 'ReturnCategory'
plt.figure(figsize=(10, 5))
corr.plot(kind='bar', width=0.9)
plt.title(f'Correlation of each column with {target_column}')
plt.xlabel('Columns')
plt.ylabel('Correlation')
plt.show()

# Instantiate the Lasso model with alpha=0.1
lasso = Lasso(alpha=0.1)

# Fit the Lasso model to the training data
lasso.fit(x_train, y_train)

# Get the coefficients of the model
coef = pd.Series(lasso.coef_, index=x.columns)

# Check if X and the number of columns in X match
assert len(coef) == len(x.columns), "Number of columns in X does not match the number of coefficients"

# Sort the coefficients by absolute value
imp_coef = coef.sort_values()

# Plot the coefficients
plt.rcParams['figure.figsize'] = (10.0, 20.0)
imp_coef.plot(kind = "barh")
plt.title("Feature importance using Lasso Model")

# Compute the mutual information between each feature and the target variable
mi = mutual_info_regression(x_train, y_train)

# Get the indices of the top k features
k = 20
top_k_indices = mi.argsort()[::-1][:k]

# Get the names of the top k features
top_k_features = x_train.columns[top_k_indices].tolist()
print('The top', k, 'features are:', top_k_features)

x_train = x_train.drop(['Product Name', 'Customer Name','Order ID'], axis=1)
x_test = x_test.drop(['Product Name', 'Customer Name','Order ID'], axis=1)

# Perform mutual information regression on the training set to determine the significance of each feature
selector = SelectKBest(lambda X, y: mutual_info_regression(X, y, discrete_features='auto'), k=15)
x_train_selected = selector.fit_transform(x_train, y_train)

# Get the feature scores and corresponding names from the selector object
feature_scores = selector.scores_
feature_names = x_train.columns.values

# Sort the feature scores and corresponding names in descending order
sorted_indices = feature_scores.argsort()[::-1]
sorted_feature_names = feature_names[sorted_indices]

# Get the top 20 most important features in descending order
top_feature_names = sorted_feature_names[:15]

# Transform x_test using the fitted selector object
x_test_selected = selector.transform(x_test)

# Get the selected feature names for x_train and x_test
selected_train_feature_names = feature_names[selector.get_support()]
selected_test_feature_names = x_test.columns[selector.get_support()]

# Print the most important features for x_train and x_test
print('The 15 most important features in descending order are:', top_feature_names)
print('The selected features for x_train are:', selected_train_feature_names)
print('The selected features for x_test are:', selected_test_feature_names)

"""Logistic Regression classifier"""

# $$$$$$$$$Logistic Regression classifier
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.model_selection import GridSearchCV

from sklearn import preprocessing
# Convert y values to categorical values
lab = preprocessing.LabelEncoder()

y_train_transformed = lab.fit_transform(y_train)
y_test_transformed = lab.fit_transform(y_test)

import warnings
# Supress the warning
warnings.filterwarnings('ignore')

# define the parameter grid
param_grid = {'estimator__C': [0.01, 0.1, 1, 10, 100],
              'estimator__penalty': ['l2','l1','elasticnet'],
              'estimator__solver': ['lbfgs','newton-cg','liblinear']}

# create a GridSearchCV object for OneVsRestClassifier
ovr_grid = GridSearchCV(OneVsRestClassifier(LogisticRegression(max_iter=100)), param_grid)
ovr_grid.fit(x_train_selected, y_train_transformed)

# create a GridSearchCV object for OneVsOneClassifier
ovo_grid = GridSearchCV(OneVsOneClassifier(LogisticRegression(max_iter=100)), param_grid)
ovo_grid.fit(x_train_selected, y_train_transformed)

# print the best parameters for each model
print('One Vs Rest best parameters:', ovr_grid.best_params_)
print('One Vs One best parameters:', ovo_grid.best_params_)

# model accuracy for Logistic Regression model
accuracy = ovr_grid.best_estimator_.score(x_test_selected, y_test_transformed)
print('One Vs Rest Logistic Regression accuracy: ' + str(accuracy))
accuracy = ovo_grid.best_estimator_.score(x_test_selected, y_test_transformed)
print('One Vs One Logistic Regression accuracy: ' + str(accuracy))

"""naive bayes"""

# #naive bayes
#naive bayes
from sklearn.naive_bayes import GaussianNB
from sklearn import preprocessing
lab=preprocessing.LabelEncoder()
y_transformed=lab.fit_transform(y_train)
labb=preprocessing.LabelEncoder()
y_transformedd=lab.fit_transform(y_test)
gnb = GaussianNB()
gnb.fit(x_train_selected,y_transformed)
y_pred = gnb.predict(x_test_selected)
print(y_pred)
from sklearn.metrics import accuracy_score
print('Model accuracy score: {0:0.4f}'. format(accuracy_score(y_transformedd, y_pred)))

"""naive bayes with grid search"""

#grid search
from sklearn.model_selection import GridSearchCV
# Define the Naive Bayes classifier
gnb = GaussianNB()
# Define the parameter grid to search
param_grid = {'var_smoothing': [1e-09, 1e-08, 1e-07, 1e-06, 1e-05]}
# Define the GridSearchCV object with 5-fold cross-validation
grid_search = GridSearchCV(estimator=gnb, param_grid=param_grid, cv=5)
# Fit the GridSearchCV object to the training data
grid_search.fit(x_train_selected, y_transformed)
# Print the best hyperparameters
print("Best hyperparameters: ", grid_search.best_params_)
# Train the Naive Bayes model with the best hyperparameters
clf = grid_search.best_estimator_
clf.fit(x_train_selected, y_transformed)

# Evaluate the performance of the model on the test data
y_pred = clf.predict(x_test_selected)
accuracy = accuracy_score(y_transformedd, y_pred)
print("Accuracy: ", accuracy)

"""XGBoost classifier"""

import xgboost as xgb

# Create an XGBoost classifier
xgb_classifier = xgb.XGBClassifier()

# Train the classifier on your training data
xgb_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = xgb_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformedd, y_pred)
print("Accuracy: ", accuracy)

import xgboost as xgb
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.datasets import load_iris


ENCODE = preprocessing.LabelEncoder()
y_train_transformed = ENCODE.fit_transform(y_train)
y_test_transformed  = ENCODE.fit_transform(y_test)

# Create an XGBClassifier object
xgb_clf = xgb.XGBClassifier()

# Define the hyperparameters and their possible values to search over
param_grid = {
    'max_depth': [3, 4, 5, 6],
    'learning_rate': [0.01, 0.1, 0.2],
    'n_estimators': [50, 100, 200],
    'gamma': [0, 0.1, 0.2, 0.3],
    'subsample': [0.5, 0.7, 1],
    'colsample_bytree': [0.5, 0.7, 1]
}

# Create a GridSearchCV object with 5-fold cross-validation
grid_search = GridSearchCV(estimator=xgb_clf, param_grid=param_grid, cv=5)

# Fit the GridSearchCV object to the training data
grid_search.fit(x_train_selected, y_train_transformed)

# Print the best hyperparameters and the corresponding score
print("Best hyperparameters: ", grid_search.best_params_)
print("Best score: ", grid_search.best_score_)

# Get the best classifier from the GridSearchCV object
best_xgb_clf = grid_search.best_estimator_

# Predict the labels of the test set using the best classifier
y_pred = best_xgb_clf.predict(x_test_selected)

# Calculate the accuracy of the classifier
accuracy = (y_pred == y_test_transformed).mean()

# Print the accuracy
print("Accuracy:", accuracy)

#testing overfit

import xgboost as xgb
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate
# Create an XGBoost classifier
xgb_classifier = xgb.XGBClassifier()

# Train the classifier on your training data
xgb_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = xgb_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformedd, y_pred)
print("Accuracy: ", accuracy)

# Evaluate the performance of the classifier using cross-validation
scores = cross_val_score(xgb_classifier, x_train_selected, y_transformed, cv=5)

# Print the mean and standard deviation of the cross-validation scores
print("Cross-validation scores: ", scores)
print("Mean cross-validation score: ", np.mean(scores))
print("Standard deviation of cross-validation scores: ", np.std(scores))
import xgboost as xgb
import numpy as np
from sklearn.model_selection import cross_validate

# Evaluate the performance of the classifier using cross-validation
cv_results = cross_validate(xgb_classifier, x_train_selected, y_transformed, cv=5, return_train_score=True)

# Print the mean training and validation scores across all the folds
print("Mean training score: ", np.mean(cv_results['train_score']))
print("Mean validation score: ", np.mean(cv_results['test_score']))

from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier

# Create a list of base classifiers
base_classifiers = [('svc', SVC()),
                    ('rf', RandomForestClassifier()),
                    ('gb', GradientBoostingClassifier())]

# Create a stacking classifier that uses logistic regression as the meta-classifier
ensemble_classifier = StackingClassifier(estimators=base_classifiers,
                                         final_estimator=LogisticRegression())

# Train the classifier on your training data
ensemble_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = ensemble_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformedd, y_pred)
print("Accuracy: ", accuracy)

# Define the parameter grid to search over
param_grid = {'n_estimators': [100, 200, 300],
              'learning_rate': [0.05, 0.1, 0.2],
              'max_depth': [3, 5, 7]}

# Instantiate the Gradient Boosting classifier
gb = GradientBoostingClassifier()

from sklearn import preprocessing
from sklearn import utils

#convert y values to categorical values
lab = preprocessing.LabelEncoder()
y_transformed = lab.fit_transform(y_train)

labb = preprocessing.LabelEncoder()
y_transformedd = lab.fit_transform(y_test)


# Create the GridSearchCV object
grid_search = GridSearchCV(estimator=gb, param_grid=param_grid, cv=5, scoring='accuracy')

# Fit the GridSearchCV object to the training data
grid_search.fit(x_train, y_transformed)

# Print the best parameters and best score
print('Best parameters:', grid_search.best_params_)
print('Best score:', grid_search.best_score_)

# Use the best model to make predictions on the test data
best_gb = grid_search.best_estimator_
y_pred = best_gb.predict(x_test)

# Calculate the accuracy of the classifier
accuracy = accuracy_score(y_transformedd, y_pred)

print('Accuracy:', accuracy)

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Create an SVM classifier
svm_classifier = SVC()

# Train the classifier on your training data
svm_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = svm_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformed, y_pred)
print("Accuracy: ", accuracy)

"""svm classifier"""

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV

# Define the hyperparameters to tune
param_grid = {'C': [0.1, 1, 10, 100],
              'gamma': [0.1, 1, 10, 100],
              'kernel': ['linear', 'rbf', 'poly']}

# Create an SVM classifier
svm_classifier = SVC()

# Use GridSearchCV to find the best hyperparameters
grid_search = GridSearchCV(svm_classifier, param_grid, cv=5)
grid_search.fit(x_train_selected, y_transformed)
best_params = grid_search.best_params_
print("Best hyperparameters: ", best_params)

# Train the classifier on your training data using the best hyperparameters
svm_classifier = SVC(**best_params)
svm_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = svm_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformed, y_pred)
print("Accuracy: ", accuracy)

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Define the hyperparameters to tune
c_values = [0.1, 1, 10, 100]
gamma_values = [0.1, 1, 10, 100]
kernel_values = ['linear', 'rbf', 'poly']

# Train and evaluate an SVM classifier for each combination of hyperparameters
best_accuracy = 0
for c in c_values:
    for gamma in gamma_values:
        for kernel in kernel_values:
            svm_classifier = SVC(C=c, gamma=gamma, kernel=kernel)
            svm_classifier.fit(x_train_selected, y_transformed)
            y_pred = svm_classifier.predict(x_test_selected)
            accuracy = accuracy_score(y_transformed, y_pred)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_params = {'C': c, 'gamma': gamma, 'kernel': kernel}

# Train the classifier on your training data using the best hyperparameters
svm_classifier = SVC(**best_params)
svm_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = svm_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformed, y_pred)
print("Accuracy: ", accuracy)

"""gmm classifier"""

from sklearn.mixture import GaussianMixture
from sklearn.metrics import accuracy_score

# Create a GMM classifier
gmm_classifier = GaussianMixture(n_components=2)

# Train the classifier on your training data
gmm_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = gmm_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformed, y_pred)
print("Accuracy: ", accuracy)

"""ensemble classifier"""

from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier

# Create a list of base classifiers
#base_classifiers = [('svc', SVC()),
 #                   ('rf', RandomForestClassifier()),
  #                  ('gb', GradientBoostingClassifier())]

# Create a list of base classifiers with regularization parameters
base_classifiers = [('svc', SVC(C=0.1)),
                    ('rf', RandomForestClassifier(max_depth=5)),
                    ('gb', GradientBoostingClassifier(max_depth=3))]

# Create a stacking classifier that uses logistic regression as the meta-classifier
ensemble_classifier = StackingClassifier(estimators=base_classifiers,
                                         final_estimator=LogisticRegression())



# Train the classifier on your training data
ensemble_classifier.fit(x_train_selected, y_transformed)

# Make predictions on your test data
y_pred = ensemble_classifier.predict(x_test_selected)
accuracy = accuracy_score(y_transformedd, y_pred)
print("Accuracy: ", accuracy)

"""RandomForestClassifier

"""

# from sklearn import preprocessing
# from sklearn import utils
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score

# ENCODE = preprocessing.LabelEncoder()
# y_train_transformed = ENCODE.fit_transform(y_train)
# y_test_transformed  = ENCODE.fit_transform(y_test)

# classifier = RandomForestClassifier(n_estimators=15, criterion="entropy")
# classifier.fit(x_train_selected, y_transformed)

# y_pred = classifier.predict(x_test_selected)
# print('Model accuracy score: {0:0.4f}'. format(accuracy_score(y_test_transformed,y_pred)))

"""Random Forest Classifier

"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.datasets import load_iris

from sklearn import preprocessing
from sklearn import utils
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

ENCODE = preprocessing.LabelEncoder()
y_train_transformed = ENCODE.fit_transform(y_train)
y_test_transformed  = ENCODE.fit_transform(y_test)


# Create a Random Forest Classifier object
rfc = RandomForestClassifier()

# Define the hyperparameters and their possible values to search over
param_grid = {
    'n_estimators': [10, 50, 100, 200],
    'max_depth': [None, 5, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}

# Create a GridSearchCV object with 5-fold cross-validation
grid_search = GridSearchCV(estimator=rfc, param_grid=param_grid, cv=5)

# Fit the GridSearchCV object to the training data
grid_search.fit(x_train_selected, y_train_transformed)

# Print the best hyperparameters and the corresponding score
print("Best hyperparameters: ", grid_search.best_params_)
print("Best score: ", grid_search.best_score_)

# Get the best classifier from the GridSearchCV object
best_rfc = grid_search.best_estimator_

# Predict the labels of the test set using the best classifier
y_pred = best_rfc.predict(x_test_selected)

# Calculate the accuracy of the classifier
accuracy = (y_pred == y_test_transformed).mean()

# Print the accuracy
print("Accuracy:", accuracy)