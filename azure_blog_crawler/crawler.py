from bs4 import BeautifulSoup
from requests_html import HTMLSession
from requests.exceptions import RequestException

from .utils import create_output_directory, write_json_file, get_articles_from_soup, process_article_content, \
    add_article_to_batch_data

JSON_OUTPUT_DIR = "json_output"


class AzureBlogCrawler:
    """Crawler class for the Azure Blog."""

    def __init__(self, first_page, batches, pages_per_batch):
        self.begin_process_page = first_page
        self.batches = batches
        self.pages_per_batch = pages_per_batch
        self.last_page_batched = first_page
        self.base_url = "https://azure.microsoft.com"
        self.blog_url = f"{self.base_url}/pt-br/blog/?Page="

    def __enter__(self):
        self.html_session = HTMLSession()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.html_session is not None:
            self.html_session.close()

    def crawl_multiple_batches(self):
        """Crawl multiple batches of blog pages."""
        for _ in range(0, self.batches):
            page_to_batch = self.last_page_batched
            self.crawl_parse_and_save_batch_pages(page_to_batch)
            self.last_page_batched = page_to_batch + self.pages_per_batch

        print("Crawling finished")

    def crawl_parse_and_save_batch_pages(self, page_to_batch):
        """Crawl, parse and save a batch of blog pages."""
        batch_data = {"articles": {}}
        page_to_crawl = page_to_batch
        for _ in range(0, self.pages_per_batch):
            print(f"Starting crawling at page {page_to_crawl}")
            self.crawl_and_parse_blog_page(page_to_crawl, batch_data)
            page_to_crawl += 1

        self.save_file_page_data(page_to_batch, batch_data)

    def crawl_and_parse_blog_page(self, page_to_crawl, batch_data):
        """Crawl a single blog page and process its articles."""
        page_response = self.get_url_content(self.blog_url + str(page_to_crawl))
        if page_response is not None:
            soup = BeautifulSoup(page_response.content, 'html5lib')
            articles = get_articles_from_soup(soup)
            self.parse_articles(articles, batch_data, page_to_crawl)
            print(f'Page {page_to_crawl} crawled and parsed.')

    def parse_articles(self, articles, batch_data, page_to_batch):
        """Parse and process a list of article elements beginning on 4th article."""
        for count, article in enumerate(articles[3:]):
            author, date_published, link, summary, title = self.extract_article_info(article)

            article_response = self.get_url_content(link)
            if article_response is not None:
                article_soup = BeautifulSoup(article_response.content, 'html5lib')
                content, position_list, tags_list = process_article_content(article_soup)

                add_article_to_batch_data(author, content, date_published, link, position_list, summary, tags_list,
                                          title, page_to_batch, count, batch_data)
                print(f'Article {count + 1} OK!')

    def get_url_content(self, url):
        """Get the content of a URL and handle exceptions."""
        try:
            return self.html_session.get(url)
        except RequestException as e:
            print(f"Error fetching URL content: {e}")
            return None

    def extract_article_info(self, article):
        """Extract relevant information from a single article element."""
        title = article.find('a', title=True).get('title')
        date_published = article.find('p', {'class': 'text-body5'}).text
        summary = article.find('p', {'lang': 'en'}).text
        href_elements = article.find_all('a', href=True)
        href = href_elements[0].get('href')
        author = href_elements[1].text
        link = f"{self.base_url}{href}"
        return author, date_published, link, summary, title

    def save_file_page_data(self, first_page_in_batch, batch_data):
        """Save batch data to a JSON file."""
        output_dir = JSON_OUTPUT_DIR
        create_output_directory(output_dir)
        last_page_in_batch = first_page_in_batch + self.pages_per_batch - 1
        file_name = f"{output_dir}/microsoft_blog_pg_{first_page_in_batch:04}_a_" \
                    f"{last_page_in_batch:04}.json"
        write_json_file(file_name, batch_data)
