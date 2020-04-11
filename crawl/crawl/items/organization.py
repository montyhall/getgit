# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Organization(scrapy.Item):
    crawlDate=scrapy.Field()
    id = scrapy.Field()
    node_id = scrapy.Field()
    url = scrapy.Field()
    repos_url = scrapy.Field()
    events_url = scrapy.Field()
    hooks_url = scrapy.Field()
    issues_url = scrapy.Field()
    members_url = scrapy.Field()
    public_members_url = scrapy.Field()
    avatar_url = scrapy.Field()
    description = scrapy.Field()

