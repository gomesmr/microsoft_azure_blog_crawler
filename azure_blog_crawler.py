import json
import os
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from requests.exceptions import RequestException


def create_output_directory(output_dir):
    """Create the output directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def write_json_file(file_name, data):
    """Write JSON data to a file."""
    with open(file_name, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class AzureBlogCrawler:
    """Crawler class for the Azure Blog."""

    def __init__(self, first_page, batches, pages_per_batch, delay_between_batches=2):
        self.begin_process_page = first_page
        self.batches = batches
        self.pages_per_batch = pages_per_batch
        self.delay_between_batches = delay_between_batches
        self.last_page_batched = self.begin_process_page
        self.page_to_batch = None
        self.base_url = "https://azure.microsoft.com"
        self.blog_url = f"{self.base_url}/pt-br/blog/?Page="
        self.batch_data = {}

    def __enter__(self):
        self.html_session = HTMLSession()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.html_session is not None:
            self.html_session.close()

    def save_file_page_data(self):
        """Save batch data to a JSON file."""
        output_dir = "json_output"
        create_output_directory(output_dir)
        file_name = f"{output_dir}/microsoft_blog_pg_{self.page_to_batch:04}_a_" \
                    f"{self.page_to_batch + self.pages_per_batch - 1:04}.json"
        write_json_file(file_name, self.batch_data)

    def crawl_multiple_batches(self):
        """Crawl multiple batches of blog pages."""
        for _ in range(0, self.batches):
            self.page_to_batch = self.last_page_batched
            self.parse_and_save_batch_pages()
            self.last_page_batched = self.page_to_batch + self.pages_per_batch

        print("Crawling finished")

    def parse_and_save_batch_pages(self):
        """Parse and save a batch of blog pages."""
        self.batch_data = {"articles": {}}
        page_to_crawl = self.page_to_batch
        for _ in range(0, self.pages_per_batch):
            print(f"Starting crawling at page {page_to_crawl}")
            self.crawl_blog(page_to_crawl)
            page_to_crawl += 1

    def crawl_blog(self, page_to_crawl):
        """Crawl a single blog page."""
        self.parse_blog_pages(page_to_crawl)
        print(f"Page {page_to_crawl} crawled.")

    def get_url_content(self, url):
        """Get the content of a URL and handle exceptions."""
        try:
            return self.html_session.get(url)
        except RequestException as e:
            print(f"Error fetching URL content: {e}")
            return None

    def parse_blog_pages(self, page_to_craw):
        """Parse a blog page and process its articles."""
        page_response = self.get_url_content(self.blog_url + str(page_to_craw))
        if page_response is not None:
            soup = BeautifulSoup(page_response.content, 'html5lib')
            articles = soup.find_all("article", class_="blog-postItem")
            self.parse_articles(articles, page_to_craw)
            self.save_file_page_data()
            print(f'Page {page_to_craw} OK!')

    def parse_articles(self, articles, page_num):
        """Parse and process a list of article elements."""
        for count, article in enumerate(articles[3:]):
            author, date_published, link, summary, title = self.extract_article_info(article)

            article_response = self.get_url_content(link)
            if article_response is not None:
                article_soup = BeautifulSoup(article_response.content, 'html5lib')
                content = article_soup.find('div', {'class': 'blog-postContent'}).text
                position_element = article_soup.find('span', {'class': 'position'})
                position = position_element.text.strip() if position_element is not None else ""
                position_list = [p.strip() for p in position.split(',')]
                tags_section = article_soup.find('div', {'class': 'blog-topicLabels'})
                if tags_section is not None:
                    tags_list = [tag.text for tag in
                                 tags_section.find_all('a', {'class': 'blog-topicLabel text-body5'})]
                else:
                    tags_list = []

                self.batch_data["articles"][f"page_{page_num}_art_{count + 1}"] = {
                    "title": title,
                    "date": date_published,
                    "summary": summary,
                    "author": author,
                    "position": position_list,
                    "tags": tags_list,
                    "content": content,
                    "link": link
                }
                print(f'Article {count + 1} OK!')

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
