from unittest.mock import Mock

import pytest

from azure_blog_crawler.crawler import AzureBlogCrawler


class TestAzureBlogCrawler:
    def test_should_create_azure_blog_crawler_instance_with_correct_arguments(self):
        first_page = 1
        batches = 3
        pages_per_batch = 5
        crawler = AzureBlogCrawler(first_page, batches, pages_per_batch)
        assert crawler.begin_process_page == first_page
        assert crawler.batches == batches
        assert crawler.pages_per_batch == pages_per_batch
        assert crawler.last_page_batched == first_page
        assert crawler.base_url == "https://azure.microsoft.com"
        assert crawler.blog_url == f"{crawler.base_url}/pt-br/blog/?Page="

    def test_should_parse_and_save_batch_pages(self):
        pass

