# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 21:03:34 2020

@author: Sylwek Szewczyk
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, pickle

class PrzepisyPl:
    
    def __init__(self, www):
        self.www = www
    
    def parse(self):
        
        database_input = {}
        lp = 0  
        
        main_res = requests.get(self.www)
        main_source = main_res.text
        main_soup = BeautifulSoup(main_source, 'html.parser')
        paths = main_soup.find_all('a', {'class': 'category-tile ng-star-inserted'}, href = True)
        
        for path in paths:
            
            url = 'https://www.przepisy.pl' + path.get('href')
            print(url)
        
            while True:
                
                res = requests.get(url)
                source = res.text
                soup = BeautifulSoup(source, 'html.parser')
                links = soup.find_all('a', {'class': 'recipe-box__title ng-star-inserted'}, href = True)
                
                for link in links:
                    if '/przepis/' in link.get('href'):
                        time.sleep(20)
                        recipe_res = requests.get(link.get('href'))
                        recipe_soup = BeautifulSoup(recipe_res.text, 'html.parser')
                        meal_name_tag = recipe_soup.find('h1', {'class':'title'})
                        meal_name = meal_name_tag.text.replace(' - VIDEO', '') if' - VIDEO' in meal_name_tag.text else meal_name_tag.text
                        img_url = recipe_soup.find('img', {'data-dont-replace': '1'}).get('src')
                        preparation_time = recipe_soup.find_all('span', {'class': 'hidden-xs'})[1].text        
                        difficulty_level_tag = [[spans.text for spans in span_tag.find_all('span') if len(spans.text) != 0][0] for span_tag in recipe_soup.find_all('li', {'title': 'Poziom trudności'})]
                        difficulty_level = difficulty_level_tag[0]
                        servings = recipe_soup.find_all('span', {'class': 'hidden-xs'})[2].text
                        ingredients = {}
                        for products in recipe_soup.find_all('li', {'class':'row-ingredient ingredient-li'}):
                            ingr_name = products.find('span', {'class': 'text-normal'}).text
                            quantity_tag = products.find('span', {'class': 'quantity pull-right'})
                            quantity = quantity_tag.text if quantity_tag else 'N/A'
                            ingredients[ingr_name] = quantity
                        for products in recipe_soup.find_all('li', {'class':'row-ingredient-product ingredient-li'}):
                            ingr_name_special = products.find('span', {'itemprop': 'recipeIngredient'}).text
                            quantity_special_tag = products.find('span', {'class': 'quantity pull-right'})
                            quantity_special = quantity_special_tag.text if quantity_special_tag else 'N/A'
                            ingredients[ingr_name_special] = quantity_special
                        preparation_steps = {}
                        for steps in recipe_soup.find_all('li', {'class': 'col-xs-12 col-sm-6 col-md-12'}):
                            step = steps.find('span', {'class': 'step-responsive-header'}).text
                            description = steps.find('div', {'itemprop': 'recipeInstructions'}).text.replace('\r\n', '')
                            preparation_steps[step] = description
                        recipe_tag = []
                        for tags in recipe_soup.find_all('div', {'class': 'normal-tags-cont'}):
                            for tag in tags.find_all('a', {'class': 'tags tag-link'}):
                                recipe_tag.append(tag.text.lower())
                    else:
                        pass
                    
                    lp += 1
                    database_input[lp] = [meal_name, preparation_time, difficulty_level, servings, ingredients, preparation_steps, recipe_tag, img_url]
                    with open('recipes.pkl', 'wb') as f:
                        pickle.dump(database_input, f)
                        
                url_tag = soup.find('a', {'class':'pagination__btn pagination__btn--arrow pagination__btn--arrow--right ng-star-inserted'})
                try:
                    #if url_tag.get('href'):
                    url = 'https://www.przepisy.pl' + url_tag.get('href')
                    print(url)
                except AttributeError:
                    break
            
        database_input_dataframe = pd.Dataframe.from_dict(database_input, orient = 'index', columns = ['Nazwa potrawy', 'Czas przygotowania', 'Stopień trudności', 'Ilość porcji', 'Składniki', 'Przepis', 'Tagi', 'Url zdjęcia'])
        return database_input_dataframe

recipes = PrzepisyPl('https://www.przepisy.pl/przepisy/dania-i-przekaski')