from azure_blog_crawler.crawler import AzureBlogCrawler

if __name__ == "__main__":
    first_page = 3
    batches = 1
    pages_per_batch = 1

    with AzureBlogCrawler(first_page, batches, pages_per_batch) as crawler:
        crawler.crawl_multiple_batches()