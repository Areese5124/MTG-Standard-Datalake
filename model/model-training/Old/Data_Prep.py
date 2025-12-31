# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 15:54:28 2025

@author: Arees
"""
def data_pre_prep ():
    import pandas as pd 
    import numpy as np
    import statistics 
    import re
    import os
    CurrentDirectory =  os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    
    PathTxt1 = 'data/ML-Data/Merged_Comp_Data.csv'
    FilePath1 = os.path.join(CurrentDirectory, PathTxt1)
    CompData = pd.read_csv(FilePath1)
    
    PathTxt2 = 'data/ML-Data/card_data.csv'
    FilePath2 = os.path.join(CurrentDirectory, PathTxt2)
    CardData = pd.read_csv(FilePath2)
    
    MLDataframe = pd.DataFrame(columns=['Card_Name', 
                                        'Decks_Played_In', 'Number_Of_Decks_Played_In',
                                        'Average_Copies_Played',
                                        'Average_Copies_Played_Mean',
                                        'Play_Percentages',
                                        'Average_Play_Percentage',
                                        'Total_Meta_Percentage_Unadjusted', 
                                        'Total_Meta_Percentage_Adjusted',
                                        ])
    
    LoopList = (CompData['Card_Name'].unique()).tolist()
    
    for i in LoopList:
        SplicedDecks = CompData.loc[CompData['Card_Name'] == i]
        DecksPlayedIn = SplicedDecks['Deck_Played_In'].tolist()
        AverageNumberPlayed =  SplicedDecks['Average_Number_Played'].tolist()
        AverageNumberPlayedMean = statistics.mean(AverageNumberPlayed)
        PlayPercentageRaw = SplicedDecks['Play_Percentage'].tolist()
        PlayPercentage = list()
        for x in PlayPercentageRaw:
           temp = int(float(re.sub(r'%', '', x)))
           PlayPercentage.append(temp) 
        PlayPercentageMean = statistics.mean(PlayPercentage)
        RawMeta = SplicedDecks['META_PERCENTAGE'].tolist()
        Meta = list()
        for x in RawMeta:
           temp = float(re.sub(r'%', '', x))
           Meta.append(temp) 
        TotalMetaPercentageUnadjusted = sum(Meta)
        AdjustedMeta = list()
        for a, b, in zip(Meta, PlayPercentage):
            AdjustedFigure = a * (b / (10**2))
            AdjustedMeta.append(AdjustedFigure)
        AdjustedMeta = sum(AdjustedMeta)
        DecksPlayedInNum = len(SplicedDecks)
        MLDataframe = pd.concat([pd.DataFrame(
                        [[i, DecksPlayedIn, DecksPlayedInNum,
                          AverageNumberPlayed, AverageNumberPlayedMean,
                          PlayPercentage, PlayPercentageMean, TotalMetaPercentageUnadjusted,
                          AdjustedMeta,]],
                        columns = MLDataframe.columns), MLDataframe], ignore_index=True)
    
    CardDataJoin = CardData[['CARD_NAME', 'KEYWORDS', 'TYPE_LINE', 'CONVERTED_MANA_COST', 
                      'MANA_COST', 'COLOR_IDENTITY', 'POWER', 'TOUGHNESS']]
    CardDataJoin.columns = ['Card_Name', 'Keywords', 'Type_Line', 'Converted_Mana_Cost', 
                      'Mana_Cost', 'Color_Identity', 'Power', 'Toughness']
    
    MLDataframe = pd.merge(MLDataframe, CardDataJoin, on = 'Card_Name')
    
    
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
    
    rows_without_basics = ~MLDataframe['Types'].str.contains('Basic', na=False)
    MLDataframe = MLDataframe[rows_without_basics]
    return(MLDataframe)

def ML_prep (DataFrame):
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    
    def string_lists_to_int_arrays (DataFrame, Column):
        unique_elements = DataFrame[Column].explode().unique()
        element_to_int = {elem: idx for idx, elem in enumerate(unique_elements, start=1)}
        DataFrame[f'{Column}'] = DataFrame[Column].apply(
                lambda lst: [element_to_int[elem] for elem in lst] if isinstance(lst, list) else []
            )
        return DataFrame
    
    def reducing_dimensions (DataFrame, Column):
        PaddedSequences = pad_sequences(
            DataFrame[f'{Column}'], 
            padding='post', 
            dtype='float32'
        )
        
        if PaddedSequences.shape[1] > 2:
            Width_Check = 3
            ColumnNames = [f'{Column}_PCA_{i+1}' for i in range(3)]
        else:
            Width_Check = 2
            ColumnNames = [f'{Column}_PCA_{i+1}' for i in range(2)]
            
        pca = PCA(n_components = Width_Check, random_state = 67)
        FittedSequences = pca.fit_transform(StandardScaler().fit_transform(PaddedSequences))
        FittedSequencesDF = pd.DataFrame(FittedSequences, columns = ColumnNames)
        FittedSequencesDF['Card_ID']= FittedSequencesDF.index
        DataFrame = pd.merge(DataFrame, FittedSequencesDF, on = 'Card_ID')
        DataFrame.drop(f'{Column}', axis=1, inplace=True)
        return DataFrame

        
    DataFrame = string_lists_to_int_arrays(DataFrame, 'Decks_Played_In')
    DataFrame = string_lists_to_int_arrays(DataFrame, 'Types')
    DataFrame = string_lists_to_int_arrays(DataFrame, 'Subtypes')
    DataFrame = string_lists_to_int_arrays(DataFrame, 'Keywords')
    DataFrame = string_lists_to_int_arrays(DataFrame, 'Mana_Cost')
    DataFrame = string_lists_to_int_arrays(DataFrame, 'Color_Identity')
    
    DataFrame = DataFrame.replace(np.nan, None)
    DataFrame = DataFrame.replace('[]', None)
    DataFrame['Card_ID']= DataFrame.index
    
    DataFrame = reducing_dimensions(DataFrame, 'Decks_Played_In')
    DataFrame = reducing_dimensions(DataFrame, 'Average_Copies_Played')
    DataFrame = reducing_dimensions(DataFrame, 'Play_Percentages')
    DataFrame = reducing_dimensions(DataFrame, 'Types')
    DataFrame = reducing_dimensions(DataFrame, 'Subtypes')
    DataFrame = reducing_dimensions(DataFrame, 'Keywords')
    DataFrame = reducing_dimensions(DataFrame, 'Mana_Cost')
    DataFrame = reducing_dimensions(DataFrame, 'Color_Identity')
    DataFrame['Power'] = DataFrame['Power'].replace('*', '-10')
    DataFrame = DataFrame.fillna(-1)
    
    return(DataFrame)
    
    



        
         
         
                 
             
             
     




         
         
         
         
         
         
         
     
     
     




    
    