from azure_blog_crawler import AzureBlogCrawler


def main():
    total_pages = 3
    pages_per_batch = 1
    delay_between_batches = 2

    crawler = AzureBlogCrawler()
    crawler.crawl_multiple_batches(total_pages, pages_per_batch, delay_between_batches)


if __name__ == '__main__':
    main()
