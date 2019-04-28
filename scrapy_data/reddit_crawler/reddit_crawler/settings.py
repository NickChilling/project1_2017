# -*- coding: utf-8 -*-

BOT_NAME = 'reddit_crawler'

SPIDER_MODULES = ['reddit_crawler.spiders']
NEWSPIDER_MODULE = 'reddit_crawler.spiders'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
DEPTH_LIMIT = 0
DOWNLOAD_DELAY = 4
ROBOTSTXT_OBEY = False
ITEM_PIPELINES = {'reddit_crawler.pipelines.JsonExportPipeline': 800,
		   }
#'reddit_crawler.pipelines.PostgresExportPipeline': 
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'reddit_crawler (+http://www.yourdomain.com)'
