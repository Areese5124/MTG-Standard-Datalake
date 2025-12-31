# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 00:13:39 2025

@author: Arees
"""
def scraper_set_up(): 
    from selenium import webdriver
    driver = webdriver.Chrome()
    print('Selenium Booted Up')
    driver.get("https://mtgdecks.net/Standard")
    driver.implicitly_wait(.5)
    print('Connected to MTG Decks')
    return (driver)

def scraping_mtg_decks_meta_data(driver):
    import pandas as pd
    from selenium.webdriver.common.by import By
    raw_html = driver.find_elements(By.CLASS_NAME, "sort")
    deck_list = list()
    for i in raw_html:
          temp = i.text
          if len(temp) == 0:
              continue
          else:
              deck_list.append(temp)
    deck_df = pd.DataFrame(columns = ['Deck_Name',  'Meta_Percentage', 
                                      'Percentage_Trend', 'Total_Number_Of_Decks',
                                      'Price',])
    more_cards = True
    while more_cards:
        temp_row = deck_list[0:5]
        if temp_row[0] ==  'ROGUE':
            temp_row.insert(2, None)
            temp_row[4] = None
            deck_df.loc[len(deck_df)] = temp_row[0:5]
            del deck_list[0:4]
        else:
            deck_df.loc[len(deck_df)] = temp_row
            del deck_list[0:5]
        if len(deck_list) == 0:
            more_cards = False
        else:
            continue
    return(deck_df)

def scraping_average_deck_makeup(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    import pandas as pd
    import re
    import time
    
    all_decks = list()
    standard_links = driver.find_elements(By.XPATH, 
    "//a[starts-with(@href, 'https://mtgdecks.net/Standard/')]"
    )
    standard_urls = [link.get_attribute('href') for link in standard_links[0:30]]
    
    for i in standard_urls:
        if 'rogue' in i:
            continue
        else:
            time.sleep(3)
        driver.get(i)
        navigation_bar = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-pills.secondary")
        archetype_widget = navigation_bar.find_element(By.XPATH, 
            "//span[@class='text-uppercase linker' and contains(text(), 'Archetype analysis')]"
                                   )
        ActionChains(driver) \
                .click(archetype_widget) \
                .perform()
        
        Time_Widget = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-pills")
        Month_Widget = Time_Widget.find_element(By.XPATH, 
                                 "//a[contains(@href, '/Standard/') and contains(@href, '/month')]")
        ActionChains(driver) \
                .click(Month_Widget) \
                .perform()
        deck_name = ((driver.find_element(By.CSS_SELECTOR, "h1")).text).removesuffix(' AVERAGE DECK')
        
        stats_numbers_web_element = driver.find_elements(By.CSS_SELECTOR, "table.table-striped td strong")
        
        deck_comp_stats_df = pd.DataFrame(columns= ['Deck_Name', 'Top_8_Appearance_Rate', 'Top_8_Win_Rate',
            ])
        stats_array = []
        for i in stats_numbers_web_element[2:]:
            i = i.text.strip()
            if len(i) == 0:
                stats_array.append(0)
            else:
                stats_array.append(int((re.search(r'[0-9]+', i)).group()))
        if stats_array[0] == 0:
            stats_array[1] = 0
        deck_comp_stats_df = pd.concat([pd.DataFrame(
            [[deck_name, stats_array[0], stats_array[1],]],  
            columns = deck_comp_stats_df.columns), deck_comp_stats_df], ignore_index=True)  
        
        Average_Number_Played_Raw = driver.find_elements(By.CSS_SELECTOR, "tr.cardItem")
        deck_package = list()
        deck_dict = pd.DataFrame(columns = ['Average_Number_Played', 'Card_Name', 
                                'Play_Percentage',])
        for i in Average_Number_Played_Raw:
            raw_string = i.text
            if len(raw_string) == 0:
                continue
            else:
                Cleaned_String = re.sub(r'([^%]+)$', "", raw_string)
                Card_Name = ((re.search(r"[^0-9]+", Cleaned_String)).group()).strip()
                Average_Number_Played = (re.search(r'^[0-9]', Cleaned_String)).group()
                Play_Percentage = (re.search(r'[0-9%.]+$', Cleaned_String)).group()
                deck_dict = pd.concat([pd.DataFrame(
                    [[Average_Number_Played, Card_Name, Play_Percentage,]],
                    columns = deck_dict.columns), deck_dict], ignore_index=True)
        deck_package.append(deck_comp_stats_df)
        deck_package.append(deck_dict)
        deck_package.append(deck_name)
        all_decks.append(deck_package)
    return (all_decks) 
        
def data_merging(decks_list, metadata):
    import pandas as pd
    concatenated_comp_data = pd.DataFrame(columns= ['Deck_Name', 'Top_8_Appearance_Rate', 'Top_8_Win_Rate',
           ]) 
    for i in decks_list:
       temp = i[0]
       concatenated_comp_data = pd.concat([concatenated_comp_data, temp], ignore_index = True)
    merged = pd.merge(metadata, concatenated_comp_data, on= 'Deck_Name', how= 'left')
    return(merged)
                
def average_deck_makeup_local_copy(deck_list):
    import json
    from datetime import date
    date = str(date.today())
    file_name = 'archetype-analysis-t30-' + date + '.json'
    file_location = '../Data/Archetype-Analysis/' + file_name
    deck_list_trimmed = list()
    for i in deck_list:  
        deck_list_spliced = i[1:]
        deck_list_spliced[0] = deck_list_spliced[0].to_json(orient = 'records')
        deck_list_trimmed.append(deck_list_spliced)
    with open(file_location, 'w') as output_file:
        json.dump(deck_list_trimmed, output_file, indent=2)
    return(file_name)

def meta_data_local_copy(metadata):
    import pandas as pd
    from datetime import date
    from pathlib import Path    
    date = (str(date.today())).replace('-','_')
    file_name = 'metadata_' + date + '.csv'
    filepath = Path('../data/Archetype-Analysis/' + file_name) 
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    metadata.to_csv(filepath, index=False)
    return(file_name)
    
 
    
    
        
            
        
    
    



    
        
        

        
        