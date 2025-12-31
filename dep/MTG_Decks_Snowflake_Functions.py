# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 11:31:54 2025

@author: Arees
"""
def database_connect (cursor):
    cursor.execute('USE WAREHOUSE COMPUTE_WH')
    print('Connected to Warehouse')
    cursor.execute('USE DATABASE STANDARD_PLAYABLE_DATASET')
    print('Connected to Database')
    cursor.execute('USE SCHEMA STANDARD_PLAYABLE_DATASET.DATA_REPO')
    print('Connected to Schema')

def average_deck_makeup_creating_json_stage(cursor):
    from datetime import date
    date = (str(date.today())).replace('-','_')
    stage_name = 'average_deck_makeup_' + date
    cursor.execute(
        "CREATE STAGE IF NOT EXISTS %s FILE_FORMAT=(TYPE='json')"
        %(stage_name,) 
                   )
    print('New stage %s created' %(stage_name,) )
    return (stage_name)

def metadata_creating_csv_stage(cursor):
    from datetime import date
    date = (str(date.today())).replace('-','_')
    stage_name = 'metadata_' + date
    cursor.execute(
        "CREATE STAGE IF NOT EXISTS %s FILE_FORMAT=(TYPE='csv')"
        %(stage_name,) 
                   )
    print('New stage %s created' %(stage_name,) )
    return (stage_name)

def loading_data_into_stage(name, stage, cursor):
    from pathlib import Path
    current_dir = Path.cwd()
    most_recent_loc = ((current_dir / '..' / 'Data/Archetype-Analysis' / name).resolve())
    most_recent_loc = str(most_recent_loc).replace('\\','/')
    cursor.execute(
        "PUT 'file://%s' @%s"
        %(most_recent_loc, stage)
        )                
    print('Successfully put %s into the stage %s' % (name, stage))
    if 'metadata' in name:
        text_file_name = '../Data/Archetype-Analysis/most_recent_metadata_dataset.txt'
        with open(text_file_name, 'w', encoding='utf-8') as file:
            file.write(name)
    else:
        text_file_name = '../Data/Archetype-Analysis/most_recent_archetype_analysis.txt'
        with open(text_file_name, 'w', encoding='utf-8') as file:
            file.write(name)
    cursor.execute( 
        "PUT 'file://%s' @TXT_REFERENCE_STAGE"
        %(text_file_name,)
        )
            
def metadata_table_creation(file_name, stage, cursor):
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS %s(
                   Deck_Name VARCHAR,
                   Meta_Percentage VARCHAR,
                   Percentage_Trend VARCHAR,
                   Total_Number_Of_Decks VARCHAR,
                   Price VARCHAR,
                   Top_8_Appearance_Rate VARCHAR,
                   Top_8_Win_Rate VARCHAR
                   )
                   ''' %(stage,))  
    cursor.execute('''
                  COPY INTO %s
                  FROM @%s/%s
                  FILE_FORMAT=(FORMAT_NAME = csv_cleaned)
                   ''' %(stage, stage, file_name,)) 
    print('worked')
    
    
    