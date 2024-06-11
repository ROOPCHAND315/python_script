from selenium import webdriver
import time
from rich import print
import math
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import traceback

import mysql.connector
class Auto_Domain_Source():
    def __init__(self):
        self.LOCAL_USERNAME='roop'
        self.LOCAL_PASSWORD='roop@12345'
        self.LIVE_USERNAME='roop'
        self.LIVE_PASSWORD='Rpn3ws!102#'
        self.type='local'                #mention here dashboard (live or local)
        self.for_sorce=True          #mention True for source and False for Doamin and xpath
        self.options=webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.driver=webdriver.Chrome(options=self.options)
  
    def read_domain_from_exel(self,domain_name=None,data_type=None):
        try:
            sheet_path='/home/roopchand/projects/newsdatafeeds/feeds_crawler/spiders_data/Spiders_Data.xlsx'

            if data_type=='doamin_name':
                df=pd.read_excel(sheet_path,sheet_name='Domains')
                domain_lists=df['Name'].to_list()
                return domain_lists
            
            elif data_type == 'domain_data':
                df2 = pd.read_excel(sheet_path, sheet_name='Domains')
                entry = df2[df2['Name'] == domain_name]
                if not entry.empty:
                    domain_data_dict = entry.to_dict(orient='records')[0]
                    return domain_data_dict
                
            elif data_type == 'xpath_data':
                df3=pd.read_excel(sheet_path,sheet_name='Xpath')
                filtered_rows = df3[(df3['Name'] == domain_name)]
                return filtered_rows
            elif data_type == 'source_data':
                df4=pd.read_excel(sheet_path,sheet_name='Sources')
                filtered_rows=df4
                return filtered_rows


        except Exception as err:
            print(f"Error reading Excel file: {err}")
            # return []        
    def open_dashboard(self):
        if self.type=='local':
            try:
                Domain_names=self.read_domain_from_exel(domain_name=None,data_type='doamin_name')
                time.sleep(1)
                self.driver.get(f'http://dashboard.newsdata.remote/newsdata_feeds/domain/')
                Username = self.driver.find_element('xpath', '//*[@id="id_username"]')
                Username.send_keys(self.LOCAL_USERNAME)
                Password = self.driver.find_element("xpath", '//*[@id="id_password"]') 
                Password.send_keys(self.LOCAL_PASSWORD)
                Log_In = self.driver.find_element("xpath", '//*[@id="login-form"]/div[3]/input')
                Log_In.click()

                if self.for_sorce:                 #for add source
                    self.add_source()
                else:    
                    for Domain_name in Domain_names:
                        add_doamin=self.driver.find_element("xpath",'//div[@id="content-main"]/ul/li/a').click()             
                        self.add_domain(Domain_name)   
                    # self.add_source()                      
            except Exception as err:
                print(f"Authentication Failed !! {err}")      
        elif self.type=='live':                                                                                              # live url
            try:
                # Domain_names=self.read_domain_from_exel(domain_name=None,data_type='doamin_name')
                # time.sleep(1)
                self.driver.get(f'http://dash115.newsdata.io/newsdata_feeds/domain/')
                Username = self.driver.find_element('xpath', '//*[@id="id_username"]')
                Username.send_keys(self.LIVE_USERNAME)
                Password = self.driver.find_element("xpath", '//*[@id="id_password"]') 
                Password.send_keys(self.LIVE_PASSWORD)
                Log_In = self.driver.find_element("xpath", '//*[@id="login-form"]/div[3]/input')
                Log_In.click()
                if self.for_sorce:                 #for add source
                    self.add_source()
                else:    
                    Domain_names=self.read_domain_from_exel(domain_name=None,data_type='doamin_name')
                    time.sleep(1)
                    for Domain_name in Domain_names:
                        Domain_name = str(Domain_name)
                        add_doamin=self.driver.find_element("xpath",'//div[@id="content-main"]/ul/li/a').click()

                        self.add_domain(Domain_name)  
                # self.add_source()
            except Exception as err:
                print(f"Authentication Failed !! {err}")      
 
    def add_domain(self, Domain_name):
        try:
            domain_name = Domain_name
            Domains_data = self.read_domain_from_exel(domain_name=domain_name, data_type='domain_data')
            names = Domains_data['Name']
            domains = Domains_data['Domain']
            display_names = Domains_data['Display_Name']
            prioritys = Domains_data['Priority']
            user_agent=Domains_data['UserAgent']
            descriptions = Domains_data['Description']

            # ... (your existing code)
            print(names)
            #Domain Name field
            name_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='id_name']"))
            )
            name_field.send_keys(names)
            # Title field 
            display_name_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="id_display_name"]'))
            )
            display_name_field.send_keys(display_names)
            # Domain field
            domain_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='id_domain']"))
            )
            domain_field.send_keys(domains)
            # Description field
            description_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@id='id_description']"))
            )
            description_field.send_keys(descriptions)
            # Connection Field
            connection = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@role='combobox']"))
            )
            connection.click()

            if self.type == 'live' or self.type == 'local':
                connection_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@class='select2-results']/ul/li[2]"))
                )
                connection_option.click()
            # Priority field
            priority_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='id_priority']"))
            )
            priority_field.send_keys(int(prioritys))
            # User-agent field
            if user_agent == "UserAgent":
                User_Agent = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@id='id_user_agent']"))
                )
                User_Agent.send_keys("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

            # Full description status 
            is_full_description_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//select[@id='id_is_full_description']/option[@value='1']"))
            )
            is_full_description_field.click()
            # proxy field
            proxy_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//select[@id='id_is_proxy']/option[@value='0']"))
            )
            proxy_field.click()

            time.sleep(1)

            self.add_xpath(domain_name)

        except Exception as e:
            print(f"Domain adding problem: {e}")

        time.sleep(1)
            

    def add_xpath(self,Domain_name):
        try:
            if self.type == 'live':
                domain_name=Domain_name
                xpath_dframe=self.read_domain_from_exel(domain_name=domain_name,data_type='xpath_data')
                # print(f"Inside addxpath {xpath_dframe}")
                fd_xpaths=xpath_dframe['Fd_Xpath'].tolist()
                fd_priority=xpath_dframe['Fd_priority'].tolist()
                image_xpaths=xpath_dframe['Image_Xpath'].tolist()
                img_priority=xpath_dframe['Img_priority'].tolist()
                if fd_xpaths and fd_priority:
                    for xpath,fd_pri in zip(fd_xpaths,fd_priority):
                        # int(input("add xpath !"))
                        time.sleep(3)
                        if isinstance(xpath, str) and not math.isnan(fd_pri):
                            add_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()]//a").click()
                            time.sleep(2)
                            # int(input("inster to next ! "))
                            send_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[2]/textarea")
                            send_xpath.send_keys(xpath)

                            fd_priority=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[6]/input[@type='number']")
                            fd_priority.clear()
                            fd_priority.send_keys(fd_pri)
                        # int(input("xpath input!!! "))    
                if image_xpaths and img_priority:
                    for xpath,img_pri in zip(image_xpaths,img_priority):
                        time.sleep(2)
                        if isinstance(xpath, str) and not math.isnan(img_pri):
                            add_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()]//a").click()
                            time.sleep(2)
                            send_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[2]/textarea")
                            send_xpath.send_keys(xpath)

                            is_img=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[5]/input[@type='checkbox']").click()                 
                            img_priority=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[6]/input[@type='number']")
                            img_priority.clear()
                            img_priority.send_keys(str(img_pri))
                            time.sleep(2)
                Save_domain=self.driver.find_element("xpath","//div[@class='submit-row']/input[@value='Save']").click()
            else:
                domain_name=Domain_name
                xpath_dframe=self.read_domain_from_exel(domain_name=domain_name,data_type='xpath_data')
                # print(f"Inside addxpath {xpath_dframe}")
                fd_xpaths=xpath_dframe['Fd_Xpath'].tolist()
                fd_priority=xpath_dframe['Fd_priority'].tolist()
                image_xpaths=xpath_dframe['Image_Xpath'].tolist()
                img_priority=xpath_dframe['Img_priority'].tolist()
                if fd_xpaths and fd_priority:
                    for xpath,fd_pri in zip(fd_xpaths,fd_priority):
                        # int(input("add xpath !"))
                        time.sleep(3)
                        if isinstance(xpath, str) and not math.isnan(fd_pri):
                            add_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()]//a").click()
                            time.sleep(2)
                            # int(input("inster to next ! "))
                            send_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[2]/textarea")
                            send_xpath.send_keys(xpath)

                            fd_priority=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[6]/input[@type='number']")
                            fd_priority.clear()
                            fd_priority.send_keys(fd_pri)
                        # int(input("xpath input!!! "))    
                if image_xpaths and img_priority:
                    for xpath,img_pri in zip(image_xpaths,img_priority):
                        time.sleep(2)
                        if isinstance(xpath, str) and not math.isnan(img_pri):
                            add_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()]//a").click()
                            time.sleep(2)
                            send_xpath=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[2]/textarea")
                            send_xpath.send_keys(xpath)

                            is_img=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[5]/input[@type='checkbox']").click()                 
                            img_priority=self.driver.find_element("xpath","(//tbody)[4]/tr[last()-2]/td[6]/input[@type='number']")
                            img_priority.clear()
                            img_priority.send_keys(str(img_pri))
                            time.sleep(2)
                Save_domain=self.driver.find_element("xpath","//div[@class='submit-row']/input[@value='Save']").click()

        except:
            print(f"Error in Xpath")
    
    def add_source(self):
        try:
            source_dataframe=self.read_domain_from_exel(domain_name=None,data_type='source_data')
            try:
                if self.type=='local':
                    Add_source=self.driver.get(f"http://dashboard.newsdata.remote/newsdata_feeds/source/add/")

                if self.type=='live':
                    Add_source=self.driver.get(f"http://dash115.newsdata.io/newsdata_feeds/source/add/")

            except Exception as error:
                print(f"[red]Login problem !  {error}") 

            for index, row in source_dataframe.iterrows():
                print(f"Row {index}:\n{row}\n")
                country=row['Country']
                # Enter domain name 
                def select_domain(domain_combobox_xpath, domain_search_xpath, domain_suggestion_xpath, domain_text, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            domain_combobox = self.driver.find_element(By.XPATH, domain_combobox_xpath)
                            domain_combobox.click()
                            # time.sleep(1.5)
                            domain_search = self.driver.find_element(By.XPATH, domain_search_xpath)
                            domain_search.click()
                            domain_search.clear()
                            domain_search.send_keys(domain_text)
                            time.sleep(1)
                            # domain_suggestion = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, domain_suggestion_xpath)))
                            # time.sleep(0.1)
                            # domain_suggestion.click()
                            try:
                                suggestion_box = WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, domain_suggestion_xpath))
                                )
                                WebDriverWait(self.driver, 10).until(
                                    lambda driver: suggestion_box.text.strip() == domain_text.strip()
                                )
                                time.sleep(1)
                                suggestion_box.click()
                                # print("Suggestion box is visible")
                                return True  # Successfully clicked suggestion
                            except Exception as e:
                                traceback.print_exc()
                                print(f"[yellow]category Error clicking suggestion: {e}")
                
                        except Exception as e:
                            print(f"[yellow]Domain name Error selecting domain: {e}")
                    print(f"[yellow]Domain name Failed to select domain after retries.")
                
                # Now, inside your try-except block:
                try:
                    select_domain("(//span[@role='combobox'])[1]",
                                  '/html/body/span/span/span[1]/input',
                                  "//span[@class='select2-results']/ul/li[1]",
                                  row['Name'])
                except Exception as err:
                    print(f"[red] domain selection failed: {err}")
                # Enter Source Field 
                def enter_text_in_field(field_xpath, text, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            field = self.driver.find_element(By.XPATH, field_xpath)
                            field.click()
                            field.clear()
                            field.send_keys(text)
                            time.sleep(0.2)  # You can replace this sleep with WebDriverWait if necessary
                            return  # Successfully entered text, exit the loop
                        except Exception as e:
                            print(f"[yellow] Source Error interacting with field: {e}")
                    print(f"[yellow]Source Failed to interact with field ({field_xpath}) after retries.")
                try:
                    enter_text_in_field("//input[@id='id_url']", row['Source_Link'])
                except Exception as err:
                    print(f"[red]Source Error entering text in field: {err}")

                # Add Language 
                def language_click_combobox(xpath, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            combobox = self.driver.find_element(By.XPATH,xpath)
                            combobox.click()
                            return  
                        except Exception as e:
                            print(f"[yellow]language Error clicking combobox: {e}")
                        time.sleep(1) 
                        print(f"language next retring 1!{_}")     
                    print(f"[yellow]language Failed to click combobox ({xpath}) after retries.")
                def language_enter_text_in_search_box(xpath, text, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            search_box = self.driver.find_element(By.XPATH,xpath)
                            search_box.click()
                            search_box.send_keys(text)
                            time.sleep(1) 
                            return
                        except Exception as e:
                            print(f"[yellow]language Error interacting with search box: {e}")
                        time.sleep(1) 
                        print(f"language next retring 2!{_}")   
                    print(f"[yellow]language Failed to interact with search box ({xpath}) after retries.")
                def click_element(xpath, by=By.XPATH):
                    try:
                        element = self.driver.find_element(by, xpath)
                        time.sleep(0.2)
                        return element
                    except Exception as e:
                        raise Exception(f"[yellow]Country Error: {e}")
                def lanugae_click_suggestion(xpath,text, max_retries=3):
                    suggestion_box_xpath=f"{xpath}/li[1]"
                    try:
                        suggestion_box = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, suggestion_box_xpath))
                        )
                        if suggestion_box.text.strip() == text.strip():
                            # time.sleep(1)
                            suggestion_box.click()
                        else:
                            suggestion_box_xpath=f"{xpath}/li[2]"
                            suggestion = click_element(suggestion_box_xpath)
                            time.sleep(1)
                            suggestion.click()
                            
                        return True  # Successfully clicked suggestion
                    except Exception as e:
                        # print(f"[yellow]category Error clicking suggestion: {e}")
                        print(f"[yellow]language Failed to click suggestion ({xpath}) after retries.")
                    time.sleep(0.5) 
                # Now, inside your loop:
   
                languages = row['Language'].split(',')
                for language in languages:
                    try:
                        language_click_combobox("(//span[@role='combobox'])[2]")
                        language_enter_text_in_search_box("(//input[@role='searchbox'])[3]", language)
                        lanugae_click_suggestion("//span[@class='select2-results']/ul",language)
                    
                       # Adjust this sleep as needed
                    except Exception as err:
                        print(f"[red] language selection failed: {err}")
                
                # Insert Country
                # def click_element(xpath, by=By.XPATH):
                #     try:
                #         element = self.driver.find_element(by, xpath)
                #         time.sleep(0.2)
                #         return element
                #     except Exception as e:
                #         raise Exception(f"[yellow]Country Error: {e}")
                def country_click_combobox(xpath, exclude_xpath=None):
                    combobox = click_element(xpath)

                    if exclude_xpath:
                        remove_button = combobox.find_elements(By.XPATH, exclude_xpath)

                        if not remove_button:
                            combobox.click()
                    else:
                        combobox.click()
                def country_click_search_box(xpath, text):
                    search_box = click_element(xpath)
                    search_box.clear()
                    search_box.send_keys(text)
                    time.sleep(2)    
                def country_click_suggestion(xpath, text):
                    suggestion_xpath = f"{xpath}/li[1]"
                    suggestion_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, suggestion_xpath))
                    )

                    time.sleep(0.5)
                    if suggestion_box.text.strip() == text.strip():
                        # time.sleep(1)
                        suggestion_box.click()
                    else:
                        suggestion_xpath = f"{xpath}/li[2]"
                        suggestion = click_element(suggestion_xpath)
                        time.sleep(0.5)
                        suggestion.click()
                        
                    time.sleep(0.5)
                # Example usage in your loop:
                countrys = row['Country'].split(',')
                count_country=[]
                for country in countrys:
                    try:
                        if country not in count_country:
                        # Specify the XPath for the removal button you want to exclude
                            remove_button_xpath = '//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul/li/span'

                            country_click_combobox(
                                xpath='//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul',
                                exclude_xpath=remove_button_xpath
                            )
                            country_click_search_box('//*[@id="source_form"]/div/fieldset/div[5]/div/div[1]/div/div/span/span[1]/span/ul/li/input', country)
                            country_click_suggestion("//span[@class='select2-results']/ul", country)
                        
                        count_country.append(country)
                        # print(count_country)
                    except Exception as err:
                        print(f"[red] Country selection failed: {err}")

                count_country.clear()        
                
                # insert Category

                def category_click_combobox(xpath, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            combobox = self.driver.find_element(By.XPATH,xpath)
                            combobox.click()
                            # time.sleep(0.2)
                            return  # Successfully clicked, exit the loop
                        except Exception as e:
                            print(f"[yellow]category Error clicking combobox: {e}")
                        # time.sleep(0.2)    
                    print(f"[yellow]category Failed to click combobox ({xpath}) after retries.")
                def category_enter_text_in_search_box(xpath, text, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            search_box = self.driver.find_element(By.XPATH,xpath)
                            search_box.click()
                            search_box.clear()
                            search_box.send_keys(str(text))
                            time.sleep(0.5)  # You can replace this sleep with WebDriverWait if necessary
                            return  # Successfully entered text, exit the loop
                        except Exception as e:
                            print(f"[yellow]category Error interacting with search box: {e}")
                        time.sleep(0.5)      
                    print(f"[yellow]category Failed to interact with search box ({xpath}) after retries.")
                def category_click_suggestion(xpath, text, max_retries=3):
                    for _ in range(max_retries):
                        try:
                            suggestion_box = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, xpath))
                            )
                            WebDriverWait(self.driver, 10).until(
                                lambda driver: suggestion_box.text.strip() == text.strip()
                            )
                            time.sleep(1)
                            suggestion_box.click()
                            return True  # Successfully clicked suggestion
                        except Exception as e:
                            pass
                            # print(f"[yellow]category Error clicking suggestion: {e}")
                        time.sleep(0.5)
                    print("[yellow]category Failed to click suggestion after retries.")


                categories = row['Category'].split(',')
                for category in categories:
                    try:
                        category_click_combobox('//*[@id="source_form"]/div/fieldset/div[6]/div/div[1]/div/div/span/span[1]/span/ul')
                        category_enter_text_in_search_box('//*[@id="source_form"]/div/fieldset/div[6]/div/div[1]/div/div/span/span[1]/span/ul/li/input', category)
                        category_click_suggestion("//span[@class='select2-results']/ul/li[1]",category)
                    except Exception as err:
                        print(f"[red] category selection failed: {err}")
                        
                if row['Collection'] == 'crypto':
                    collection_crypto = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "(//select[@id='id_custom_api_ids'])[1]/option[2]"))
                    )
                    collection_crypto.click()

                save_and_another_button = self.driver.find_element("xpath", '//*[@id="source_form"]/div/div/input[2]').click()
                # save_button.click()
                try:
                    status_false = self.driver.find_element("xpath", "//*[@id='source_form']/div/p")
                    status_false_text = status_false.text
                    if status_false_text:
                        break                 
                except:             
                    status_True = self.driver.find_element("xpath", '//*[@id="content-start"]/ul/li')
                    status_True_text = status_True.text
                    if status_True_text:
                        print(f"Added source Successfully!{self.type}")

            
        except Exception as ee:
            print(f"[red]error{ee}")
      


obj=Auto_Domain_Source()
# obj.add_source()  
obj.open_dashboard()