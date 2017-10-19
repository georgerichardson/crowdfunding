# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from babel.numbers import parse_decimal, parse_number

from crowdfunding.items import Fundraiser

def parse_currency_value(string):
    try:
        value = parse_number(string)
        return value
    except:
        try:
            value = parse_decimal(string)
            return value
        except:
            return 0

def parse_date(string):
    string = ' '.join(c.split(' ')[1:])
    return datetime.strptime(string, '%B %d, %Y')

class CrowdriseFundraiserSpider(scrapy.Spider):
    name = 'crowdrise'
    allowed_domains = ['crowdrise.com']
    start_urls = ['http://crowdrise.com/']
    
    def __init__(self, categories=None, page_limit=None):
        self.page_limit = page_limit
        self.categories = categories
        self.site_sections = ['orphanage']

    def start_requests(self, response):
        if self.categories:
            urls = ['http://www.crowdrise.com/search/project-results/null/null/{}/null'.format(self.category) for categories in self.categories]
        else:
            urls = ['http://www.crowdrise.com/search/project-results/null/null/{}/null'.format(self.category) for categories in self.site_sections]
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse_search_page)

    def parse_search_page(self, response):
        next_page = '//div[contains(@class,"fRight pagination marginTop40")]//a[last()]/@href'
        next_page = reponse.xpath(next_page).extract()
        fundraisers = response.xpath('//div[contains(@class,"items fLeft clearfix")]/h3/a/@href').extract()

        for fundraiser in fundraisers:
            yield scrapy.Request(response.urljoin(fundraiser),
                                 callback=self.parse_fundraiser)

        if next_page:
            if self.page_limit:
                if (int(next_page.split('/')[-1][0]) 
                        <= self.page_limit):
                    yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_search_page)
            else:
                yield scrapy.Request(response.urljoin(next_page),
                                    callback=self.parse_search_page)

    def parse_fundraiser(self, response):
        url = response.url
        if 'fundraiser' in url.split('/'):
            page_type = 'individual'

        else:
            page_type = 'team'
            title = response.xpath('//h1/text()').extract()

            amount_goal = '//h3[contains(@class,"inline goal")]/text()'
            amount_goal = response.xpath(amount_goal).extract_first()
            amount_goal = currency_value(amount_goal.split(' ')[1][1:])

            amount_raised = '//h2[contains(@class,"inline raised")]/text()'
            amount_raised = response.xpath(amount_raised).extract_first()
            amount_raised = currency_value(amount_raised[1:])

            created_at = '//div[contains(@class,"row")]//h6[contains(text(),"Created")]/text()'
            created_at = response.xpath(created_at).extract()
            created_at = parse_date(created_at)

