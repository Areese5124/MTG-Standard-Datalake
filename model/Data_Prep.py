# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 12:03:36 2025

@author: Arees
"""
#Gradient Boosted Decision Trees using a Bag of Words model

#def data_pre_prep ():
import pandas as pd 
import numpy as np
import statistics 
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

CurrentDirectory =  os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))


PathTxt1 = 'data\ML-Data\Merged_Comp_Data.csv'
FilePath1 = os.path.join(CurrentDirectory, PathTxt1)
CompData = pd.read_csv(FilePath1)

PathTxt2 = 'data\ML-Data\card_data.csv'
FilePath2 = os.path.join(CurrentDirectory, PathTxt2)
CardDataRaw = pd.read_csv(FilePath2)
Trim = ['SET_NAME','COLORS']
MLDataframe = CardDataRaw.drop(columns = Trim, axis=1)

MLDataframe.columns =['Card_Name', 'Converted_Mana_Cost', 'Mana_Cost', 'Color_Identity', 
                      'Keywords', 'Card_Text', 'Power', 'Toughness', 'Type_Line' ]


CompCardList = (MLDataframe['Card_Name'].unique()).tolist()

CardDataRaw['Played_In_Comp'] = np.where(MLDataframe[
    'Card_Name'].isin(CompCardList), 1, 0)

#Cleaning up Types 
TypeDF = pd.DataFrame(columns = ['Index', 'Types', 'Subtypes'])

for row in MLDataframe.itertuples():
    SubTypeCheck = re.search(r'[—]', row.Type_Line)
    if SubTypeCheck is None: 
       Types = row.Type_Line.split()
       SubTypes = None
    else:
        Types = (((re.search(r"^[^—]+", row.Type_Line)).group()).strip()).split()
        SubTypes = (((re.search(r"(?<=—).*", row.Type_Line)).group()).strip()).split()
    TypeDF = pd.concat(
        [pd.DataFrame([[row.Index, Types, SubTypes,]], columns = TypeDF.columns), TypeDF]) 

TypeDF = TypeDF.set_index('Index')
MLDataframe = pd.merge(MLDataframe, TypeDF, left_index=True, right_index=True, how='inner')
MLDataframe.drop('Type_Line', axis=1, inplace=True)

#Cleaning up Keywords
KeywordDF = pd.DataFrame(columns = ['Index', 'Keywords'])
for row in MLDataframe.itertuples():
     KeywordString = re.findall(r'[\w\s]+', row.Keywords)
     if KeywordString != None:
         KeywordList = list()
         for i in KeywordString:
             keyword = i.strip()
             if len(keyword) > 0:
                 KeywordList.append(keyword)
         KeywordDF = pd.concat(
             [pd.DataFrame([[row.Index, KeywordList,]], columns = KeywordDF.columns), KeywordDF]) 

KeywordDF = KeywordDF.set_index('Index')
MLDataframe.drop('Keywords', axis=1, inplace=True)
MLDataframe = pd.merge(MLDataframe, KeywordDF, left_index=True, right_index=True, how='inner')

#Cleaning up Mana Cost
ManaCostDF = pd.DataFrame(columns = ['Index', 'Mana_Cost'])
for row in MLDataframe.itertuples():
     ManaCostString = str(row.Mana_Cost)
     if ManaCostString != 'nan':
         ManaCostStringList = re.findall(r'[\w]+', ManaCostString)
         ManaList = list()
         for i in ManaCostStringList:
             Mana = i.strip()
             if Mana.isdigit():
                 Mana = int(Mana)
                 itr = 0
                 while itr < Mana:
                     ManaList.append('Gen')
                     itr += 1
             else:
                 ManaList.append(Mana)
         ManaCostDF = pd.concat(
             [pd.DataFrame([[row.Index, ManaList,]], columns = ManaCostDF.columns), ManaCostDF])
     else:
         ManaList = None
         ManaCostDF = pd.concat(
             [pd.DataFrame([[row.Index, ManaList,]], columns = ManaCostDF.columns), ManaCostDF])

ManaCostDF = ManaCostDF.set_index('Index')
MLDataframe.drop('Mana_Cost', axis=1, inplace=True)
MLDataframe = pd.merge(MLDataframe, ManaCostDF, left_index=True, right_index=True, how='inner')

#Cleaning Up Color Identity
ColorIdentityDF = pd.DataFrame(columns = ['Index', 'Color_Identity'])
for row in MLDataframe.itertuples():
     ColorIdentityString = re.findall(r'[\w]+', row.Color_Identity)
     if ColorIdentityString != None:
         ColorIdentityList = list()
         for i in ColorIdentityString:
             keyword = i.strip()
             if len(keyword) > 0:
                 ColorIdentityList.append(keyword)
         ColorIdentityDF = pd.concat(
             [pd.DataFrame([[row.Index, ColorIdentityList,]], columns = ColorIdentityDF.columns), ColorIdentityDF]) 

ColorIdentityDF = ColorIdentityDF.set_index('Index')
MLDataframe.drop('Color_Identity', axis=1, inplace=True)
MLDataframe = pd.merge(MLDataframe, ColorIdentityDF, left_index=True, right_index=True, how='inner')

RowsWithoutBasics = ~MLDataframe['Types'].str.contains('Basic', na=False)
MLDataframe = MLDataframe[RowsWithoutBasics]

MLDataframe['Card_Text'] = MLDataframe['Card_Text'].replace(np.nan, '')

EnglishStopwords = set(stopwords.words('english'))

def remove_stopwords(text):
    WordTokens = word_tokenize(text)
    SentenceFiltered = [w for w in WordTokens if not w.lower() in EnglishStopwords]
    return " ".join(SentenceFiltered)

MLDataframe['Card_Text'] = MLDataframe['Card_Text'].apply(remove_stopwords)































