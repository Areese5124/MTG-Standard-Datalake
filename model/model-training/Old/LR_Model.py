# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 13:34:45 2025

@author: Arees
"""
#Boiler Plate
from Data_Prep import data_pre_prep
from Data_Prep import ML_prep

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
#------------------------------------------------------------------  
UnPreppedMLDataFrame = data_pre_prep()
MLDataFrame = ML_prep(UnPreppedMLDataFrame)
CardNameWithId = MLDataFrame[['Card_Name', 'Card_ID']]
MLDataFrame.drop('Card_Name', axis=1, inplace=True)

X = MLDataFrame.drop('Card_ID', axis=1)
Y = MLDataFrame['Card_ID']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y,
                                                    test_size=0.3, random_state=42)

model = LinearRegression()
model.fit(X_train, Y_train)
Y_pred = model.predict(X_test)
mse = mean_squared_error(Y_test, Y_pred)
r2 = r2_score(Y_test, Y_pred)

print(f"Mean Squared Error: {mse:.2f}")
print(f"R-squared: {r2:.2f}")

print(f"Coefficient (slope): {model.coef_[0]:.2f}")
print(f"Intercept: {model.intercept_:.2f}")

plt.figure(figsize=(6, 4))
plt.scatter(Y_test, Y_pred, color='pink')
plt.xlabel("Actual Card ID")
plt.ylabel("Predicted Card ID")
plt.title("Actual vs. Predicted Card ID")
plt.plot([min(Y), max(Y)], [min(Y), max(Y)], color='crimson', linestyle='-') # 45-degree line
plt.show()