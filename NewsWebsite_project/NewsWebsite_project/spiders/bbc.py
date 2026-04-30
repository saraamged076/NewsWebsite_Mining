from urllib import response

import scrapy


class BbcSpider(scrapy.Spider):
    name = "bbc"

    start_urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    ]

    custom_settings = {
        "CLOSESPIDER_ITEMCOUNT": 500,
        "DOWNLOAD_DELAY": 0.3
    }

    def parse(self, response):
        for item in response.css("item"):
            link = item.css("link::text").get()
            category = response.url.split("/news/")[1].split("/")[0]

            yield scrapy.Request(
                link,
                callback=self.parse_article,
                meta={"category": category}
            )

    def parse_article(self, response):
        title = response.css("h1::text").get()
        paragraphs = response.css("article p::text").getall()

        content = " ".join(paragraphs)

        if not title or len(content) < 100:
            return

        yield {
            "url": response.url,
            "title": title,
            "content": content,
            "links": response.css("a::attr(href)").getall(),  # Get all links in the article
            "category": response.meta.get("category", "unknown")  # get category from meta, default to "unknown" if not available
        }

    
        for link in response.css("a::attr(href)").getall():
            if "/news/" in str(link):
                yield response.follow(
                    link,
                    callback=self.parse_article,
                    meta={"category": response.meta.get("category", "unknown")}
                )