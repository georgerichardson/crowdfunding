# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrowdfundingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CrowdriseTeamFundraiser(scrapy.Item):
    page_type = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    amount_goal = scrapy.Field()
    amount_raised = scrapy.Field()
    created_at = scrapy.Field()
    beneficiary = scrapy.Field()
    beneficiary_url = scrapy.Field()
    description = scrapy.Field()
