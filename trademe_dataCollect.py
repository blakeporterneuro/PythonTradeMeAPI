# -*- coding: utf-8 -*-

# This program will use TradeMe.co.nz's API to search listings and aggregate the listing data for later analysis

# By Dr. Blake Porter
# 28/04/2018

# Useful search values
# Regions
# 1 Auckland
# 2 Bay of Plenty
# 3 Canterbury
# 4 Gisborne
# 5 Hawke's Bay
# 6 Manawatu
# 7 Narkborough
# 8 Nelson
# 9 Northland
# 10 Otago
# 11 Southland
# 12 Taranaki
# 14 Waikato
# 15 Wellington
# 16 West Coast

# Districts
# 68 Waitaki
# 69 Central Otago
# 70 Queenstown-Lakes
# 71 Dunedin
# 72 Clutha
# 79 South Otago
# 83 Wanaka

#Import needed libraries
from requests_oauthlib import OAuth1Session # for authenicating 
import time # for delaying our requests
import json # for organizing our data
import pandas as pd # for storing our data

# Keys (found on your TradeMe account page)
consumerKey = 'yourKeyHereAsAString'
consumerSecret = 'yourKeySecretHereAsAString'

# Easy way to get these here: https://developer.trademe.co.nz/api-overview/authentication/
oAuthToken = 'yourTokenHereAsAString'
oAuthSecret = 'yourTokenSecretHereAsAString'

# Use oAuth to authenticate ourselves with our keys and tokens
tradeMe = OAuth1Session(consumerKey,consumerSecret,oAuthToken,oAuthSecret)

# Tradme uses HTTP for get requests, meaning you ask for specific data by putting in a long URL
searchUrlDunedin = 'https://api.trademe.co.nz/v1/Search/Property/Residential.json?adjacent_suburbs=false&date_from=2018-04-12T01%3A10&district=71&open_homes=false&page=1&photo_size=Thumbnail&return_metadata=false&rows=500&sort_order=Default HTTP/1.1'

# Get the page we are searching for
returnedPageAll = tradeMe.get(searchUrlDunedin)

# Get out the conent of that page
dataRawAll = returnedPageAll.content

# Convery it to JSON format
parsedDataAll = json.loads(dataRawAll)

# Total number of listings
totalCount = parsedDataAll['TotalCount']

totalRequests = int(totalCount/500)

for i in range(0,totalRequests+1):
    # Convert the current page number to a string
    pageNum = str(i)
    
    # Add our current page to the search URL
    searchAll = 'https://api.trademe.co.nz/v1/Search/Property/Residential.json?adjacent_suburbs=false&date_from=2018-04-12T01%3A10&district=71&open_homes=false&page=' + pageNum + '&photo_size=Thumbnail&return_metadata=false&rows=500&sort_order=Default HTTP/1.1'

    # Use our authenticator to return our search
    returnedPageAll = tradeMe.get(searchAll)
    
    # Get page contents
    dataRawAll = returnedPageAll.content
    
    # Convert it to JSON format
    parsedDataAll = json.loads(dataRawAll)
    
    # Get the listings
    eachListingAll = parsedDataAll['List']
    
    # Convert to Pandas dataframe
    pandaAll = pd.DataFrame.from_dict(eachListingAll)
    
    # Save data
    if i == 0: # If we are on the first page, create a new file to store our data
        pandaAll.to_pickle('dataDunedin.pkl')
    else: # Otherwise, if we are on a subsequent page, append our existing file with subsequent results

        # Load from storage
        pandaAllStorage = pd.read_pickle('dataDunedin.pkl')
    
        # Append storaged with new data
        pandaAllStorage = pandaAllStorage.append(pandaAll,ignore_index=True)

        # Save (will overwrite old stored data)
        pandaAllStorage.to_pickle('dataDunedin.pkl')
    # End if statement

    time.sleep(0.5)
    print(pageNum + ' out of ' + str(totalRequests))

print('All pages saved')
