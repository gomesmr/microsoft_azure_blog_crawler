import json
import os
import shutil
import tempfile

from azure_blog_crawler.utils import create_output_directory, write_json_file, get_articles_from_soup, \
    process_article_content, add_article_to_batch_data


class TestUtils:

    def test_should_create_output_folder_if_it_doesnt_exists(self):
        test_directory = "test_dir"

        # Verifique se o diretório não existe antes de criar
        assert not os.path.exists(test_directory), f"O diretório {test_directory} já existe."

        # Cria o diretório
        create_output_directory(test_directory)

        # Verifica se o diretório foi criado
        assert os.path.exists(test_directory), f"O diretório {test_directory} não foi criado."

        # Remove o diretório criado no final do teste
        shutil.rmtree(test_directory)

        # Verifica se o diretório foi removido
        assert not os.path.exists(test_directory), f"O diretório {test_directory} não foi removido."

    def test_should_write_json_file(self):
        # 1. Stub do arquivo que será gravado
        data = {"key": "value"}

        # 2. Cria um diretório temporário para gravar o arquivo
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = os.path.join(temp_dir, "test_file.json")

            # 3. Gravação propriamente dita
            write_json_file(file_name, data)

            # 4. Lê o arquivo e verifica sua integridade
            with open(file_name, "r", encoding='utf-8') as f:
                loaded_data = json.load(f)

            assert loaded_data == data

    def test_should_get_articles_from_soup(self):
        from bs4 import BeautifulSoup
        with open("stubs/page_3_blog_azure.html", "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html5lib')
        articles = get_articles_from_soup(soup)
        assert len(articles) == 13

    def test_should_process_article_content_correctly(self):
        from bs4 import BeautifulSoup
        with open("stubs/article_content_blog_azure.html", "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html5lib')
        processed_content, position_list, tags_list = process_article_content(soup)
        expected_content = "Extract robust insights from image and video content with Azure Cognitive Service for " \
                           "Vision\n\nWe are pleased to announce the public preview of Microsoft’s Florence " \
                           "foundation model, trained with billions of text-image pairs and integrated as " \
                           "cost-effective, production-ready computer vision services in Azure Cognitive Service for " \
                           "Vision."
        assert expected_content in processed_content
        assert position_list == ["Technical Fellow", "Cloud and AI"]
        assert tags_list == ["Announcements", "Cognitive Services", "Artificial Intelligence"]

    def test_should_add_article_to_batch_data_correctly(self):
        input_data = {
            "author": "John Doe",
            "content": "Lorem ipsum dolor sit amet...",
            "date_published": "2023-04-09",
            "link": "https://example.com/article",
            "position_list": ["Author"],
            "summary": "Lorem ipsum dolor sit amet...",
            "tags_list": ["Tag1", "Tag2"],
            "title": "Lorem ipsum dolor sit amet",
            "page_to_batch": 3,
            "count": 0,
            "batch_data": {"articles": {}}
        }
        expected_output = {
            "articles": {
                "page_3_art_1": {
                    "title": "Lorem ipsum dolor sit amet",
                    "date": "2023-04-09",
                    "summary": "Lorem ipsum dolor sit amet...",
                    "author": "John Doe",
                    "position": ["Author"],
                    "tags": ["Tag1", "Tag2"],
                    "content": "Lorem ipsum dolor sit amet...",
                    "link": "https://example.com/article"
                }
            }
        }
        add_article_to_batch_data(**input_data)
        assert input_data["batch_data"] == expected_output
