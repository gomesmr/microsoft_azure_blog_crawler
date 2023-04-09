from azure_blog_crawler.crawler import AzureBlogCrawler

if __name__ == "__main__":
    first_page = 13
    batches = 2
    pages_per_batch = 2

    with AzureBlogCrawler(first_page, batches, pages_per_batch) as crawler:
        crawler.crawl_multiple_batches()