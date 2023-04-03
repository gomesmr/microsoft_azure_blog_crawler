from requests_html import HTMLSession
from bs4 import BeautifulSoup
import time
import json


def blog_crawler(first_page, num_pages):
    global content
    url = "https://azure.microsoft.com/pt-br/blog/?Page="
    URL = "https://azure.microsoft.com/"
    inicio = time.time()
    data = {"articles": {}}
    session = HTMLSession()
    for i in range(first_page, first_page + num_pages):
        next_page = i
        r1 = session.get(url + str(next_page))
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
                link = URL + href
                r2 = session.get(URL + href)
                article = BeautifulSoup(r2.content, 'html5lib')
                content = article.find('div', {'class': 'blog-postContent'}).text
                position = article.find('span', {'class': 'position'}).text.strip()
                position_list = [p.strip() for p in position.split(',')]
                tags = article.find('div', {'class': 'blog-topicLabels'})
                tags_list = [tag.text for tag in tags.find_all('a', {'class': 'blog-topicLabel text-body5'})]
                data["articles"][f"page_{next_page}_{count}"] = {
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
    with open(f"microsoft_blog_pg_{first_page}_a_{first_page+num_pages-1}.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

