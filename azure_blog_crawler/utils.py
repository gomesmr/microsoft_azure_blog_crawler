import json
import os


def create_output_directory(output_dir):
    """Create the output directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def write_json_file(file_name, data):
    """Write JSON data to a file."""
    with open(file_name, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_articles_from_soup(soup):
    """Extracts articles from the batch page"""
    return soup.find_all("article", class_="blog-postItem")


def process_article_content(article_soup):
    """Extracts information of each article in batch"""
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
    return content, position_list, tags_list


def add_article_to_batch_data(author, content, date_published, link, position_list, summary, tags_list, title,
                              page_to_batch, count, batch_data):
    """Parse article data to dict and add article info's to the batch data."""
    article_dict = {
        "title": title,
        "date": date_published,
        "summary": summary,
        "author": author,
        "position": position_list,
        "tags": tags_list,
        "content": content,
        "link": link
    }
    batch_data["articles"][f"page_{page_to_batch}_art_{count + 1}"] = article_dict
