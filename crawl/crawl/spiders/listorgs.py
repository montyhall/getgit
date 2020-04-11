import scrapy
from scrapy import signals
from scrapy.spiders import CrawlSpider
import json
import os
import pandas as pd
import urllib.parse
from crawl.items.organization import Organization
from datetime import datetime

'''
scrape OPEN orgs in Github

https://api.github.com/organizations?since=1

see: https://developer.github.com/v3/orgs/

scrapy crawl getorgs \
-a statsFile=stats.json \
-a errorFile=errors.txt \
-a failedFile=failed.txt \
-o orgsdata.json

'''
class CrawlerSpider(CrawlSpider):
    name = "getorgs"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''
        from_crawler is often used for getting a reference to the crawler object
        (that holds references to objects like settings, stats, etc) and then
        either pass it as arguments to the object being created or set attributes to it.
        :param crawler:
        :param args:
        :param kwargs:
        :return:
        '''
        spider = super(CrawlerSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self,
                 statsFile: str = 'stats.json',
                 errorFile: str = 'errors.txt',
                 failedFile: str='failed.txt') -> None:

        self.statsDir = 'stats'

        self.gitBase = 'https://api.github.com/'
        self.query = 'organizations'
        self.query = urllib.parse.urljoin(self.gitBase, self.query)

        self.statsFile = os.path.join(self.statsDir, statsFile)
        os.makedirs(os.path.dirname(self.statsFile), exist_ok=True)

        self.failedurls = os.path.join(self.statsDir, failedFile)
        os.makedirs(os.path.dirname(self.failedurls), exist_ok=True)

        self.errorFile = os.path.join(self.statsDir, errorFile)
        os.makedirs(os.path.dirname(self.errorFile), exist_ok=True)

        self.errors_fp = open(self.errorFile, 'w')
        self.failed_fp = open(self.failedurls, 'w')

        super(CrawlerSpider, self).__init__()

    def readSeeds(self,seedsFile: str) -> pd.DataFrame:
        return pd.read_json(seedsFile,orient='index').transpose()

    def spider_opened(self,spider):
        """ Handler for spider_closed signal. see:
        https://doc.scrapy.org/en/latest/topics/signals.html
        """
        self.logger.info('Spider opened: {}'.format(spider.name))
        self.crawler.stats.set_value('failed_search_url_count', 0)
        self.crawler.stats.set_value('failed_detailed_url_count', 0)

    def spider_error(self,spider):
        self.errors_fp.write(spider.failure+'\n')

    def spider_closed(self,spider):
        """ Handler for spider_closed signal. see:
        https://doc.scrapy.org/en/latest/topics/signals.html
        pandas.read_json('injuries.json')
        """
        #self.crawler.stats.set_value('failed_urls', len(self.failed_urls))

        with open(self.statsFile, 'w') as fp:
            d=self.crawler.stats.get_stats()
            d['start_time']=d['start_time'].isoformat()
            d['finish_time']=d['finish_time'].isoformat()
            json.dump(d, fp)

        self.errors_fp.close()
        self.failed_fp.close()

        spider.logger.info('Spider closed: %s', spider.name)

    def start_requests(self,page: int=1) -> None:
        q = self.query + "?since={}".format(page)
        yield scrapy.Request(url=q,
                             callback=self.parse,
                             errback=self.pagination_error,
                             meta={'since':page})

    def parse(self, response):
        # get agent links on 1 result page
        linkobj = response.headers['link'].decode('utf-8')
        if linkobj:
            parts = linkobj.split(',')
            link = parts[0]
            if 'rel="next"' in link:
                nextUrl = link[link.find("<") + 1:link.find(">")]
                page = int(nextUrl.split('since=')[1].strip())
                yield scrapy.Request(url=nextUrl,
                                     callback=self.parse,
                                     errback=self.pagination_error,
                                     meta={'since': page})

        orgs = json.loads(response.body_as_unicode())

        if orgs:
            for org in orgs:
                orgObj = Organization()
                orgObj['crawlDate'] = datetime.now().isoformat()
                orgObj['id'] = org['id']
                orgObj['node_id'] = org['node_id']
                orgObj['url'] = org['url']
                orgObj['repos_url'] = org['repos_url']
                orgObj['events_url'] = org['events_url']
                orgObj['hooks_url'] = org['hooks_url']
                orgObj['issues_url'] = org['issues_url']
                orgObj['members_url'] = org['members_url']
                orgObj['public_members_url'] = org['public_members_url']
                orgObj['avatar_url'] = org['avatar_url']
                orgObj['description'] = org['description']
                yield orgObj

    def parseDetailPage(self,response):
        yield self.get_detail_page_info(response)


    def pagination_error(self,failure):
        self.crawler.stats.inc_value('failed_detailed_url_count')
        url = failure.value.response.url
        self.failed_fp.write(url+'\n')
