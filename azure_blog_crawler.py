import os
import json
import time
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def save_file_page_data(data, first_page, num_pages):
    output_dir = "json_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = f"{output_dir}/microsoft_blog_pg_{first_page:04}_a_{first_page + num_pages - 1:04}.json"
    with open(file_name, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class AzureBlogCrawler:

    def __init__(self, first_page, batches, pages_per_batch, delay_between_batches=2):
        self.begin_process_page = first_page
        self.batches = batches
        self.pages_per_batch = pages_per_batch
        self.delay_between_batches = delay_between_batches
        self.base_url = "https://azure.microsoft.com/"
        self.blog_url = f"{self.base_url}pt-br/blog/?Page="
        self.html_session = HTMLSession()
        self.blog_response_data = {"articles": {}}

    def crawl_multiple_batches(self):
        for page in range(0, self.batches, self.pages_per_batch):
            print(f"Starting crawling at page {self.begin_process_page + page}")
            self.crawl_blog(page + 1)
            if page + self.pages_per_batch < self.batches:
                print(f"Waiting {self.delay_between_batches} seconds before the next batch")
                time.sleep(self.delay_between_batches)

        print("Crawling finished")

    def crawl_blog(self, first_page):
        start_time = time.time()
        self.parse_blog_pages(first_page, self.pages_per_batch)
        end_time = time.time()
        print("Duration of process {:.3f}s".format(end_time - start_time))
        save_file_page_data(self.blog_response_data, self.begin_process_page, self.pages_per_batch)

    def get_url_content(self, url):
        return self.html_session.get(url)

    def parse_blog_pages(self, first_page, num_pages):
        for page_num in range(self.begin_process_page + first_page - 1,
                              self.begin_process_page + first_page + num_pages - 1):
            page_response = self.get_url_content(self.blog_url + str(page_num))
            soup = BeautifulSoup(page_response.content, 'html5lib')
            articles = soup.find_all("article", class_="blog-postItem")
            self.parse_articles(articles, page_num)
            print(f'Page {page_num} OK!')

    def parse_articles(self, articles, page_num):
        for count, article in enumerate(articles[3:]):
            title = article.find('a', title=True).get('title')
            date_published = article.find('p', {'class': 'text-body5'}).text
            summary = article.find('p', {'lang': 'en'}).text
            href_elements = article.find_all('a', href=True)
            href = href_elements[0].get('href')
            author = href_elements[1].text
            link = f"{self.base_url}{href}"

            article_response = self.get_url_content(link)

            article_soup = BeautifulSoup(article_response.content, 'html5lib')
            content = article_soup.find('div', {'class': 'blog-postContent'}).text
            position_element = article_soup.find('span', {'class': 'position'})
            position = position_element.text.strip() if position_element is not None else ""
            position_list = [p.strip() for p in position.split(',')]
            tags_section = article_soup.find('div', {'class': 'blog-topicLabels'})
            tags_list = [tag.text for tag in tags_section.find_all('a', {'class': 'blog-topicLabel text-body5'})]
            self.blog_response_data["articles"][f"page_{page_num}_art_{count + 1}"] = {
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
