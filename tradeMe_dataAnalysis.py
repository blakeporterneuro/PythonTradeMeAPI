# -*- coding: utf-8 -*-

# This program analyze the listings collected from trademe.co.nz's API and stored in a Panda's dataframe to find out the best price to pay

# By Dr. Blake Porter
# 28/04/2018

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import ensemble
import webbrowser


# Load data
dataAll = pd.read_pickle('dataDunedin.pkl') # load all data

# What data do we want to keep from the listing?
labels = ['LandArea','Area','Bedrooms','Bathrooms','PriceDisplay','PropertyType','ListingId'] # specify data we want to use

# Only keep the columns (labels) we want to use
data = dataAll[labels] 

# Trademe doesn't provide the starting price of real estate
# Rather, it provides 'PriceDisplay' which is a chracter string 
# This is up to the TradeMe poster as what it contains
# e.g "Offers over $500,000"
# We want to extract only the numerical price from these strings

# Get the PriceDisplay data
priceStrings = dataAll['PriceDisplay'] 

# Replace anything that is not a digit with nothing (aka delete it)
priceInt = priceStrings.str.replace(r'(\D+)','') 

# Convert the remaining digits, which are still characters to python, to numbers 
priceInt = pd.to_numeric(priceInt) 

# Replace old strings with new numbers
data.PriceDisplay = priceInt 

# Clean up data (up to you if you want to do this, and if you want to do it before or after the analysis below)
data = data.dropna(axis = 0,how = 'any') # Remove any entry where we are missing data

# Get rid of 0's and 1's. For example, if there is no price, it defaults to 1. No houses are actually going for a dollar! Simiilarly, land size may be empty, no houses are on 0 m^3
data = data[(data != 0).all(1)] # Remove 0's

dataDescribe = data.describe() # This function describes all our data and give us useful information, such as means, min, max

# we can use all this data to clean up the data to fit our needs
data = data[data['Bedrooms'] <= 5] # Only houses with 5 bedrooms or less
data = data[data['PriceDisplay'] <= 700000] # Asking prices within your budget!
data = data[data['LandArea'] <= 5000] # To remove huge places, like farms
data = data[data['Area'] <= 500] # No huge homes

# Do some basic analysis
# Simple plots
sns.set_palette("dark");
plt.figure()
sns_plot = sns.distplot(data['PriceDisplay']).set_title("Price histogram")
sns_plot.figure.savefig("Price.png")

plt.figure()
sns_plot = sns.regplot(x='Area',y='PriceDisplay',data=data).set_title("House area vs Price")
sns_plot.figure.savefig("AreaByPrice.png")

plt.figure()
sns_plot = sns.regplot(x='Bedrooms',y='PriceDisplay',data=data,x_jitter=.1).set_title("Bedrooms vs Price")
sns_plot.figure.savefig("BedByPrice.png")

plt.figure()
sns_plot = sns.regplot(x='Bathrooms',y='PriceDisplay',data=data,x_jitter=.1).set_title("Bathrooms vs Price")
sns_plot.figure.savefig("BathByPrice.png")

# More complex plots
plt.figure()
sns_plot = sns.jointplot(x=data['PriceDisplay'], y=data['Area'], kind="hex");
sns_plot.figure.savefig("AreaByPricePretty.png")

plt.figure()
sns_plot = sns.pairplot(data,hue='Bedrooms',palette="PuBuGn_d")
sns_plot.figure.savefig("pairPlot.png")

# Correlation to see how data is related 
correlations = data.corr()
fig = plt.figure()
plt.set_cmap('jet')
ax = fig.add_subplot(111)
cax=ax.matshow(correlations,vmin=-1,vmax=1)
fig.colorbar(cax)
ticks=np.arange(0,len(labels)-1,1) # the -3 is there to ignore the last 3 series, which are categories 
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.set_xticklabels(labels[0:5])
ax.set_yticklabels(labels[0:5])
plt.show()


# Model our data
y = data['PriceDisplay'] # we want to get the price out and set it to y. y is what we want the model to determine based on the inputs, X
X = data.drop('PriceDisplay',axis=1) # we drop price from our data and set it to X. X are our inputs which the model will use to try to reach y
X = X.drop('ListingId',axis=1)

# The modelwe are going to use can only use numerical data, so we need to handle our Categorical data
# Pandas lets us easily convert various strings to true/false or 1/0 values
# It will create new coloumns and give each listing a 1 or 0 for that column
# E.g. a house will go from "House" to a 1 in the house column
# While a "Townhome" will be 0 for house and 1 for townhome
X=pd.get_dummies(X,columns=['PropertyType'], drop_first=True)

# Next we split our data so the model can train on some portion of our data, then test what it learned on a different portion
xTrain,xTest,yTrain,yTest = train_test_split(X,y,train_size=0.90,shuffle=True)

# Train the model
reg = LinearRegression()
reg.fit(xTrain,yTrain)

# Check our score of how well the test data could be predicted with our model
reg.score(xTest,yTest)

# Predict values using the test data
predictions = pd.Series(reg.predict(X)) # Use our model to predict the price of all our data 
predictions = predictions.rename('Predictions') # just rename the Series to predictions 
y = y.rename('Real') # rename our real price data 
y = y.reset_index(drop=True)  
listingIds = data['ListingId'].reset_index(drop=True) # get listingIds 
comparisons = pd.concat([y, predictions, listingIds],axis=1) # Add together our real prices and predicted data into one dataframe called comparison

comparisons['Difference'] = comparisons['Real'] - comparisons['Predictions'] # create a new series in our dataframe which is the difference in predicted price versus real price

fig = plt.figure()
sns_plot = sns.regplot('Real','Predictions',data=comparisons).set_title("Real vs Predicted price")
sns_plot.figure.savefig("realvpredict.png")

fig = plt.figure()
sns_plot = sns.regplot('Real','Difference',data=comparisons).set_title("Real price vs Predicted difference")
sns_plot.figure.savefig("realdiff.png")

# Get the deals!
goodDeals = comparisons[comparisons['Difference'] <= -100000] # Only keep big differences
goodDeals = goodDeals.reset_index(drop=True)  

link_count = 0 # initialize link count
for link_number in range(len(goodDeals)):   
    webbrowser.get().open('https://www.trademe.co.nz/Browse/Listing.aspx?id='+str(goodDeals.ListingId[link_number]))
    link_count += 1 # count the number of links we have opened
    if link_count == 9: #if 10 links have been opened (we start at 0)
        input('Press enter to continue opening links') #wait for user to press enter
        link_count = 0 #reset link_count to 0

# GradientBoostingRegressor
clf = ensemble.GradientBoostingRegressor(n_estimators=100,max_depth=5,min_samples_split =2,learning_rate = 0.1, loss = 'ls')
clf.fit(xTrain,yTrain)
clf.score(xTest,yTest)

