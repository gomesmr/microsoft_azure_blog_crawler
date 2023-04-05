from azure_blog_crawler import AzureBlogCrawler


if __name__ == "__main__":
    first_page = 1
    batches = 2
    pages_per_batch = 3
    delay_between_batches = 2

    with AzureBlogCrawler(first_page, batches, pages_per_batch, delay_between_batches) as crawler:
        crawler.crawl_multiple_batches()