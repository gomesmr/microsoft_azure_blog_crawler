from azure_blog_crawler import AzureBlogCrawler


def main():
    begin_process_on_page = 1
    batches = 1
    pages_per_batch = 1

    crawler = AzureBlogCrawler(begin_process_on_page, batches, pages_per_batch)
    crawler.crawl_multiple_batches()


if __name__ == '__main__':
    main()
