import pandas as pd
import numpy as np
import requests 
class filter_source:
    def __init__(self, sheet_path):
        self.sheet_path = sheet_path
        self.df=None
    
    def get_sheet_source(self):
        try:
            self.df = pd.read_excel(self.sheet_path, sheet_name='common')
            return self.df
        except Exception as err:
            print(f"Error reading Excel file: {err}")
        
    def get_intersection_source(self):
        try:
            data_frame = self.get_sheet_source()
            already_exist_source_list = self.df['Already_exist_source'].to_list()
            get_sources_list = self.df['get_sources'].to_list()
            response_get_source_list=[]
            count=0
            for url in get_sources_list:
                try:
                    count=count+1
                    print(count)
                    response = requests.get(url)
                    print(response.url)
                    response_get_source_list.append(response.url)
                except:
                    response_get_source_list.append(url)
            print(f"{response_get_source_list}")

            intersection = set(already_exist_source_list).intersection(get_sources_list)

            # Ensure length of intersection matches length of DataFrame
            intersection_list = pd.Series(list(intersection))
            if len(intersection_list) == len(self.df):
                self.df = self.df.assign(Intersection_source=intersection_list)
            else:
                new_col = pd.Series(list(intersection) + [np.nan] * abs(len(self.df) - len(intersection)))
                self.df = self.df.assign(Intersection_source=new_col)
            self.df.to_excel(self.sheet_path, sheet_name='common', index=False)
            self.get_difference_source()
        except Exception as err:
            print(f"Error getting intersection: {err}")
            
    def get_difference_source(self):
        try:
            df = self.get_sheet_source()
            already_exist_source_set = set(df['Already_exist_source'])
            get_sources_set = set(df['get_sources'])
            difference_get_sources_set = pd.Series(list(get_sources_set - already_exist_source_set)).reindex(df.index, fill_value=np.nan)

            self.df['get_difference_source'] = difference_get_sources_set
            self.df.to_excel(self.sheet_path, sheet_name='common', index=False)
            print(f"save successfully!")
        except Exception as err:
            print(f"Error getting difference: {err}")
    
sheet_path = "/home/roopchand/test/scrapyTest/feedFinder/feedFinder/scripts/sheets/get_common_source.xlsx"
obj = filter_source(sheet_path)
obj.get_intersection_source()
# obj.get_difference_source()
