# -*- coding: utf-8 -*-
import re
import scrapy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from babel.numbers import parse_decimal, parse_number

from crowdfunding.items import CrowdriseFundraiser

def parse_team_currency_value(string):
    try:
        value = parse_number(string)
        return value
    except:
        try:
            value = parse_decimal(string)
            return value
        except:
            return 0

def parse_team_date(string):
    string = ' '.join(string.split(' ')[1:])
    return datetime.strptime(string, '%B %d, %Y')

def parse_relative_date(possible_dates):
    if not possible_dates:
        return datetime.today()
    for d in possible_dates:
        for period in ['day', 'month', 'year']:
            s = re.search('(\d+)( {})'.format(period), d)
            if s:
                duration = int(s.groups()[0])
                if period == 'month':
                    return datetime.now() - relativedelta(months=duration)
                elif period == 'year':
                    return datetime.now() - relativedelta(years=duration)
                else:
                    return datetime.now() - relativedelta(days=duration)


class CrowdriseFundraiserSpider(scrapy.Spider):
    name = 'crowdrise'
    allowed_domains = ['crowdrise.com']
    start_urls = ['https://crowdrise.com/']
    
    def __init__(self, categories=None, page_limit=None):
        self.page_limit = page_limit
        self.categories = categories
        self.site_sections = ['orphanage']

    def start_requests(self):
        if self.categories:
            urls = ['https://www.crowdrise.com/search/project-results/null/null/{}/null'.format(category) for category in self.categories]
        else:
            urls = ['https://www.crowdrise.com/search/project-results/null/null/{}/null'.format(category) for category in self.site_sections]
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse_search_page)

    def parse_search_page(self, response):
        next_page = '//div[contains(@class,"fRight pagination marginTop40")]//a[last()]/@href'
        next_page = response.xpath(next_page).extract_first()
        fundraisers = response.xpath('.//div[contains(@class,"items fLeft clearfix")]/h3/a/@href').extract()

        for fundraiser in fundraisers:
            yield scrapy.Request(response.urljoin(fundraiser),
                                 callback=self.parse_fundraiser)

        if next_page:
            if self.page_limit:
                if (int(next_page.split('/')[-1][0]) 
                        <= int(self.page_limit)):
                    yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_search_page)
            else:
                yield scrapy.Request(response.urljoin(next_page),
                                    callback=self.parse_search_page)

    def parse_fundraiser(self, response):
        url = response.url
        if 'fundraiser' in url.split('/'):
            page_type = 'fundraiser'

            title = response.xpath('//h3[contains(@class, "padL10")]/text()').extract_first()

            amount_goal = '//p[contains(@class, "progressText")]//text()'
            amount_goal = response.xpath(amount_goal).extract_first()
            if amount_goal:
                amount_goal = parse_team_currency_value(amount_goal.split(' ')[-1][1:])
            else:
                amount_goal = 0

            amount_raised = '//div[contains(@id, "total_raised")]/h3//text()'
            amount_raised = response.xpath(amount_raised).extract_first()
            amount_raised = parse_team_currency_value(amount_raised[1:])

            created_at = '//div[contains(@class, "title fLeft")]//p//i//text()'
            created_at = response.xpath(created_at).extract()
            created_at = parse_relative_date(created_at)

            description = '//div[@id="content"]//p//text()'
            description = response.xpath(description).extract()
            description = ' '.join(description)

            beneficiary = '//p[@id="benefiting_line"]//a/text()'
            beneficiary = response.xpath(beneficiary).extract_first()
            beneficiary_url = '//p[@id="benefiting_line"]//a/@href'
            beneficiary_url = response.xpath(beneficiary_url).extract_first()

        else:
            page_type = 'team fundraiser'
            title = response.xpath('//h1/text()').extract()

            amount_goal = '//h3[contains(@class,"inline goal")]/text()'
            amount_goal = response.xpath(amount_goal).extract_first()
            amount_goal = parse_team_currency_value(amount_goal.split(' ')[1][1:])

            amount_raised = '//h2[contains(@class,"inline raised")]/text()'
            amount_raised = response.xpath(amount_raised).extract_first()
            amount_raised = parse_team_currency_value(amount_raised[1:])

            created_at = '//div[contains(@class,"row")]//h6[contains(text(),"Created")]/text()'
            created_at = response.xpath(created_at).extract_first()
            created_at = parse_team_date(created_at)

            description = '//div[contains(@class, "tab-text")]//p//text()'
            description = response.xpath(description).extract()
            description = ' '.join(description)
            
            beneficiary = '//div[@class="row clickable-user-row" and descendant::span[contains(., "Benefiting Charity")]]//p[@class="organizer-name"]/text()'
            beneficiary = response.xpath(beneficiary).extract_first()
            beneficiary_url = '//div[@class="row clickable-user-row" and descendant::span[contains(., "Benefiting Charity")]]//a/@href'
            beneficiary_url = response.xpath(beneficiary_url).extract_first()

            
        fundraiser = CrowdriseFundraiser(
                url = url,
                page_type = page_type,
                title = title,
                amount_goal = amount_goal,
                amount_raised = amount_raised,
                created_at = created_at,
                beneficiary = beneficiary,
                beneficiary_url = beneficiary_url,
                description = description
                )

        yield fundraiser

