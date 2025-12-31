# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 15:15:57 2025

@author: Arees

"""
#Boiler Plate
import sys
from pathlib import Path
main_dir = str(Path(__file__).parent.parent)
sys.path.append(main_dir)

from dep.MTG_Decks_Scraper_Functions import scraper_set_up
from dep.MTG_Decks_Scraper_Functions import scraping_mtg_decks_meta_data
from dep.MTG_Decks_Scraper_Functions import scraping_average_deck_makeup
from dep.MTG_Decks_Scraper_Functions import data_merging
from dep.MTG_Decks_Scraper_Functions import average_deck_makeup_local_copy
from dep.MTG_Decks_Scraper_Functions import meta_data_local_copy
from dep.Snowflake_Login import snowflake_login
from dep.MTG_Decks_Snowflake_Functions import database_connect
from dep.MTG_Decks_Snowflake_Functions import average_deck_makeup_creating_json_stage
from dep.MTG_Decks_Snowflake_Functions import loading_data_into_stage
from dep.MTG_Decks_Snowflake_Functions import metadata_creating_csv_stage
from dep.MTG_Decks_Snowflake_Functions import metadata_table_creation
#------------------------------------------------------------------  
selenium_cursor = scraper_set_up()
metadata = scraping_mtg_decks_meta_data(selenium_cursor)
average_deck_makeup_raw = scraping_average_deck_makeup(selenium_cursor)
selenium_cursor.quit()
metadata_merged = data_merging(average_deck_makeup_raw, metadata)
metadata_file_name = meta_data_local_copy(metadata_merged)
average_deck_makeup_file_name = average_deck_makeup_local_copy(average_deck_makeup_raw)

cursor = snowflake_login()
database_connect(cursor)

metadata_stage_name = metadata_creating_csv_stage(cursor)
loading_data_into_stage(metadata_file_name, metadata_stage_name, cursor)
metadata_table_creation(metadata_file_name, metadata_stage_name, cursor)

average_deck_makeup_stage_name = average_deck_makeup_creating_json_stage(cursor)
loading_data_into_stage(average_deck_makeup_file_name,
                                            average_deck_makeup_stage_name, cursor) 





  