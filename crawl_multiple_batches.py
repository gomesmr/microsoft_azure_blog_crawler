import time

from crawler import blog_crawler


def crawl_multiple_batches():
    total_pages = 9
    pages_per_batch = 3
    delay_between_batches = 2

    for i in range(0, total_pages, pages_per_batch):
        print(f"Crawling batch starting at page {i + 1}")
        blog_crawler(i + 1, pages_per_batch)
        if i + pages_per_batch < total_pages:
            print(f"Waiting {delay_between_batches} seconds before next batch")
            time.sleep(delay_between_batches)

    print("Crawling completed")