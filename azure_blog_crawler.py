from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time
import json


class AzureBlogCrawler:

    def __init__(self):
        self.url = "https://azure.microsoft.com/pt-br/blog/?Page="
        self.URL = "https://azure.microsoft.com/"

    def blog_crawler(self, first_page, num_pages):
        global content
        inicio = time.time()
        data = {"articles": {}}
        session = HTMLSession()
        for i in range(first_page, first_page + num_pages):
            next_page = i
            r1 = session.get(self.url + str(next_page))
            pag = BeautifulSoup(r1.content, 'html5lib')

            lista = pag.find_all("article", class_="blog-postItem")
            count = 0
            for i, item in enumerate(lista):
                if i < 3:
                    pass
                else:
                    title = item.find('a', title=True).get('title')
                    data_pub = item.find('p', {'class': 'text-body5'}).text
                    summary = item.find('p', {'lang': 'en'}).text
                    href_a = item.find_all('a', href=True)
                    href = href_a[0].get('href')
                    author = href_a[1].text
                    link = self.URL + href
                    r2 = session.get(link)
                    article = BeautifulSoup(r2.content, 'html5lib')
                    content = article.find('div', {'class': 'blog-postContent'}).text
                    position = article.find('span', {'class': 'position'}).text.strip()
                    position_list = [p.strip() for p in position.split(',')]
                    tags = article.find('div', {'class': 'blog-topicLabels'})
                    tags_list = [tag.text for tag in tags.find_all('a', {'class': 'blog-topicLabel text-body5'})]
                    data["articles"][f"page_{next_page}_art_{count + 1}"] = {
                        "title": title,
                        "date": data_pub,
                        "summary": summary,
                        "author": author,
                        "position": position_list,
                        "tags": tags_list,
                        "content": content,
                        "link": link
                    }
                    count += 1
                    print(f'Artigo {i} OK!')
            print(f'Pagina {next_page} OK!')
        fim = time.time()
        print(fim - inicio)
        with open(f"json_output/microsoft_blog_pg_{first_page:04}_a_{first_page + num_pages - 1:04}.json", "w",
                  encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def crawl_multiple_batches(self, total_pages, pages_per_batch, delay_between_batches):
        for page in range(0, total_pages, pages_per_batch):
            print(f"Iniciando Crawling na página {page + 1}")
            self.blog_crawler(page + 1, pages_per_batch)
            if page + pages_per_batch < total_pages:
                print(f"Aguardando {delay_between_batches} segundos antes do próximo batch")
                time.sleep(delay_between_batches)

        print("Crawling finalizado")
