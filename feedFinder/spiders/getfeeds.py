import scrapy
import pandas as pd
from rich import print
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin, urlparse
from scrapy.selector.unified import Selector
from xlsxwriter import Workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
# from scrapy.spidermiddlewares.httperror import HttpError
# from scrapy.utils.python import global_object_name
import logging
import tldextract
from feedFinder.settings import WEBSHARE_URL
import time
# import sys
# sys.set_coroutine_origin_tracking_depth(2000)
import twisted.internet.error
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class GetfeedsSpider(scrapy.Spider):
    name = 'getfeeds'
    custom_settings = {
        # 'ROBOTSTXT_OBEY': True,
        # 'DOWNLOAD_DELAY': 3,
        'RETRY_TIMES': 2,
        'DOWNLOAD_TIMEOUT': 15,
        # 'CONCURRENT_REQUESTS': 8,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
        # },
        # 'HTTPCACHE_ENABLED': True,
        # 'HTTPCACHE_EXPIRATION_SECS': 0,
        # 'HTTPCACHE_DIR': 'httpcache',
        # 'HTTPCACHE_IGNORE_HTTP_CODES': [301,302,403],
        # 'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
        # 'LOG_LEVEL': 'INFO',
        # 'COOKIES_ENABLED': False,
        # 'RETRY_ENABLED': False,
        # 'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',

    }
    def __init__(self):
        # self.user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
        # self.user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) Qt/4.8.5 Safari/534.34'
        # self.user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        self.user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        # self.user_agent=''
        self.is_proxy =  1   # SET '1' FOR ACTIVE PROXY ELSE 0
        self.is_robotTxt =0   #SET '1' FOR dont_obey_robotstxt =FALSE AND '0' FOR dont_obey_robotstxt =TRUE

 #robots.txt as a set of rules that websites use to tell web crawlers, like search engine bots, which parts of their site they're allowed to visit and scrape.When dont_obey_robotstxt is set to True, it's like telling the Scrapy spider to ignore those rules completely. So, even if the website says "Don't scrape this page," the spider will go ahead and scrape it anyway.

        self.domain_df = pd.read_excel('/home/roopchand/test/scrapyTest/feedFinder/feedFinder/scripts/sheets/collect_data_sheet.xlsx', sheet_name='Data')
        self.base_url=''
        self.home_page_feed=[]
        self.all_feed_link=[]
        self.domain_data=[]
        self.headers = {}  
        # self.options=webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        # self.driver=webdriver.Chrome(options=self.options)
    def start_requests(self):
        domain_urls=self.domain_df['Domain'].tolist()
        self.source=[]
        meta_options = {}
        if self.is_proxy == 1:
            meta_options['proxy'] = WEBSHARE_URL["WEBSHARE_URL_HTTP"]
        if self.is_robotTxt == 0:          
            meta_options['dont_obey_robotstxt'] = True

        for domain_url in domain_urls:
            if pd.notna(domain_url):
                try:
                    meta_options['domain_url']=domain_url
                    yield scrapy.Request(domain_url,
                                        meta=meta_options if meta_options else None,
                                        headers={"User-Agent": self.user_agent} if self.user_agent else None,
                                        callback=self.getall_link, 
                                        )
                except Exception as error:
                    self.logger.error(f"Requesting Error: {domain_url}: {error}")
            else:
                self.logger.warning(f"[red] Ignoring NaN value in domain_url: {domain_url}")

    def getall_link(self, response):
        domain_url = response.meta['domain_url']
        self.base_url=response.url
        # title = response.url.replace('https://', '').replace('http://', '').replace('.com', '').replace('/', '').replace('www.',
        # '').replace('.',' ').title()
        title = response.xpath('//title/text()').get()
        description = response.xpath('//meta[@name="description"]/@content').get()
        if description is None or len(description) == 0:
            description = "Description not available"
        if title is None or len(title) == 0:
            title="title not available"

        # try:    
        #     self.driver.get('https://tranco-list.eu/query')
        #     Domain_name=response.url.replace('https://', '').replace('http://', '').replace('www.','')
        #     if Domain_name.endswith('/'):
        #         Domain_name.replace('/','')
        #     priority=self.driver.find_element("xpath","//input[@id='domainInput']")   
        #     priority.send_keys(Domain_name)
        # except Exception as err:
        #     print(f"Priority error {err}")    
        name=response.url.replace('https://', '').replace('http://', '').replace('.com', '').replace('/', '').replace('www.','').replace('.',' ').replace(' ','_')
        domain_entry = {'Domain_name':name,'Domain': domain_url,'Display_name':title,'Description':description, 'source': []}
        # print(f"[red]     name: {name},    title: {title},    Discription: {description}")            69
        home_rssfeed = response.xpath('//link[@rel="alternate" and @type="application/rss+xml"]/@href').extract()
        if home_rssfeed:
            rssfeed = [urljoin(self.base_url, link) if link.startswith('/') else link for link in home_rssfeed]
            for link in rssfeed:
                 if 'comments/' not in link and 'author/' not in link:
                    if link not in domain_entry['source']:
                        domain_entry['source'].append(link)
                        
        link_extractor = LinkExtractor(tags=('a','span'),attrs=('href',))
        all_links = [link.url for link in link_extractor.extract_links(response)]   
        all_filtered_links = [urljoin(response.url, link) for link in all_links]
        def is_valid_url(url):
            parsed_url = urlparse(url)
            return all([parsed_url.scheme, parsed_url.netloc])
        valid_urls = [url for url in all_filtered_links if is_valid_url(url)]
        def filter_links_by_domain(base_url, links):
            base_domain = tldextract.extract(base_url).domain
            filtered_links = [link for link in links if tldextract.extract(link).domain == base_domain] 
            return filtered_links   
        filtered_links = filter_links_by_domain(self.base_url, valid_urls)
        filtered_links.append(urljoin(self.base_url, '/rss'))
        for link in filtered_links:
            try: 
                yield scrapy.Request(link, 
                                     headers={"User-Agent": self.user_agent} if self.user_agent else None, 
                                     callback=self.parse_all_link,meta={'domain_entry': domain_entry})
            except Exception as error:
                self.logger.error(f"Parsing Error: {link}: {error}") 

    def parse_all_link(self, response):   
        try:         
            if '/rss' in response.url:
                domain_entry = response.meta['domain_entry']
                items = response.xpath('//channel/item | //feed/entry')
                if items:
                    domain_entry['source'].append(response.url)
                    if domain_entry not in self.domain_data:
                        self.domain_data.append(domain_entry) 
                else:
                    print("[red]--------------------------Add Xpath for get rss collection----------------------------------")
                    # If all RSS feeds are in one page, you can add an XPath to get all relevant feeds
                    get_feed_collection = response.xpath("//body/div[@class='page-wrapper container mt-0 mt-md-4']/div[@class='container mt-0 md-4 mb-md-4 mainPageContainer py-3']/div[@id='wrapper']/div[@id='content']/div[@id='c2577']/div[1]/div[3]//a/@href").extract()
                    for feed in get_feed_collection:
                        if feed.startswith('http'):
                            yield scrapy.Request(feed, 
                                             headers={"User-Agent": self.user_agent} if self.user_agent else None,
                                              callback=self.parse_feed_link,
                                              meta={'domain_entry': domain_entry})
                    
            else:
                domain_entry = response.meta['domain_entry']
                # print(f"[bright_cyan]----------------------------------PARSE_LINK ------------------")
                rss_links = response.xpath('//link[@rel="alternate" and @type="application/rss+xml"]/@href').extract()
                rss_links = [urljoin(self.base_url, link) if link.startswith('/') else link for link in rss_links if 'comments/' not in link and 'author/' not in link]
                self.home_page_feed.extend(rss_links)
                rss_links=list(set(self.home_page_feed))
                # self.logger.info(f"rss_links Links: {rss_links} {len(rss_links)}")
                print(f"[blue]  rss_links Links: {rss_links} {len(rss_links)} ")
                if rss_links:
                    for link in rss_links:
                        if link.startswith('http'):
                            yield scrapy.Request(link,
                                              headers={"User-Agent": self.user_agent} if self.user_agent else None,
                                              callback=self.parse_feed_link, 
                                              meta={'domain_entry': domain_entry})
        except Exception as error:
            print("Parse link error:", error)
    def parse_feed_link(self, response):  
        try:
            print(f"[bright_yellow].................................... PARSEFEEDLINK....................................")
            domain_entry = response.meta['domain_entry']
            selector = Selector(response=response)
            selector.remove_namespaces()
            items = response.xpath('//channel/item | //feed/entry')
            count_item = 0
            for item in items:
                title = item.xpath('title/text()').get()
                pubDate = item.xpath('pubDate/text() | pubdate/text() | updated/text()').get()
                link = item.xpath('link/text() | link/@href').get()
                if title and pubDate and link:
                    count_item += 1       
            if count_item >=4:
                if response.url not in domain_entry['source']: 
                    domain_entry['source'].append(response.url)
                    print(f"[red]sources-> {domain_entry['source']}")                         
        except Exception as error:
            print("Final parse feed error:", error)

        if domain_entry not in self.domain_data:
            self.domain_data.append(domain_entry) 
        # print(f"final feeds {self.domain_data}{domain_entry['source']}")     
    def closed(self, reason):
        # print(f"After close feeds {self.domain_data}")   
        if hasattr(self.crawler.engine.slot.scheduler.df, 'clear'):
            self.crawler.engine.slot.scheduler.df.clear()
        if len(self.domain_data)==0:
            print(f"Not feed found ! ")  
        else:
            # Iterate through each row in self.domain_data
            # print(f"domain_feed {self.domain_data}")
            data=list(set(self.domain_data[0]['source']))
            self.domain_data[0]['source']=data 
            df = pd.DataFrame(self.domain_data)
            df = df.explode('source')
            df = df[['Domain_name','Domain', 'Display_name', 'Description', 'source']]
            domain=df['Domain'].to_list()
            def extract_domain(url):
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
                return domain
            n=len(domain)
            try:
                # Domain_name = str(domain[1]).replace('https://', '').replace('http://', '').replace('www.', '').replace('/', '')
                filtered_domain = extract_domain(str(domain[1]))
                print(f"Processed domain name: {filtered_domain}")
                # Initialize WebDriver (Ensure the driver executable is in your PATH)
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                service = Service()
                service.log_path = "/dev/null"
                driver = webdriver.Chrome(service=service,options=options)
                driver.get('https://tranco-list.eu/query')

                # Use explicit waits to handle timing issues
                wait = WebDriverWait(driver, 10)

                priority = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='domainInput']")))
                priority.send_keys(filtered_domain)
                search = driver.find_element(By.XPATH, "//button[@id='getRanks']")
                search.click()
                time.sleep(5)
                # Wait until the result appears
                result = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@id='rank']")))
                domain_priority = result.text
                print(f"Domain priority: {domain_priority}")
                # time.sleep(5)
                # Ensure 'n' and 'df' are defined and pri_list is correctly formed
                pri_list = [domain_priority] * n
                df.insert(3, 'Priority', pd.Series(pri_list))

            except Exception as err:
                print(f"Priority error: {err}")
            finally:
                driver.quit()

                print(f"Updated DataFrame: {df}") 
          

            # Write the DataFrame to an Excel file
            
            with pd.ExcelWriter('/home/roopchand/test/scrapyTest/feedFinder/feedFinder/scripts/sheets/collect_data_sheet.xlsx', engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            
                # Get the workbook and the worksheet
                workbook = writer.book
                worksheet = writer.sheets['Data']            
                # Add formatting to header
                header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)           
                # Set column width
                for i, col in enumerate(df.columns):
                    column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(i, i, column_len)
            
            print("Excel file 'collect_data_sheet.xlsx' has been created successfully.")

# # if __name__ == "__main__":
# #     process = CrawlerProcess(get_project_settings())
# #     process.crawl(GetfeedsSpider)
# #     process.start()