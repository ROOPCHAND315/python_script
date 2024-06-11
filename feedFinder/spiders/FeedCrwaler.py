# import scrapy
# from typing import Generator
# from feedFinder.settings import WEBSHARE_URL

# class FeedCrwaler(scrapy.spiders):
#     name='feedcrwaler'
    
#     def __init__(self,*args, **kwargs):
#         self.user_agent=''
#         self.is_proxy =  0   # SET '1' FOR ACTIVE PROXY ELSE 0
#         self.is_robotTxt =0   #SET '1' FOR dont_obey_robotstxt =FALSE AND '0' FOR dont_obey_robotstxt =TRUE 
#         self.feed_urls = []
#         super().__init__(**kwargs)
    
#     def get_request_obj(self,url,is_feed:bool=False):
#         meta_options = {}
#         if self.is_proxy == 1:
#             meta_options['proxy'] = WEBSHARE_URL["WEBSHARE_URL_HTTP"]
#         if self.is_robotTxt == 0:          
#             meta_options['dont_obey_robotstxt'] = True
#         if is_feed:
#             self.feed_urls.append(url)

#         return scrapy.Request(url,dont_filter = True, meta = meta_options if meta_options else None,
#                               headers = {"User-Agent": self.user_agent} if self.user_agent else None,
#                               errback = self.failed_feed if is_feed == True else self.failed_url,
#                               callback = self.parse_feed if is_feed == True else self.parse_url,
#                               )  
#     def start_requests(self,)->Generator[scrapy.Request,None,None]:  
#         if not self.start_urls:
#             raise AttributeError("Crawling could not start: 'start_urls' not found ""or empty (but found 'start_url' attribute instead, ""did you miss an 's'?)")
#         for url in self.start_urls:
#             yield self.get_request_obj(url=url,is_feed=self.is_feed_scraper)
        
