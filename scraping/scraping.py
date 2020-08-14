from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import requests
from db import create_connection
from db import (
    articles,
    services,
    urls
)
from start_urls import all_start_urls


UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
)
session = requests.Session()
session.headers.update({"User-agent": UA})
TIMEOUT = 30

connection = create_connection()

def extract_urls(text, current_service, current_url):

    bs = BeautifulSoup(text, "lxml")
    container = bs.find(class_="gl_plugin listing")

    items = container.find_all("a")
    for item in items:

        try:
            url = item.attrs.get("href", "")

            if url.startswith("//lublin.se"):
                url = urljoin(current_url, url)
                url_components = {"url": url, "service": current_service}
                urls.add_urls(connection, url_components)
            elif url.startswith("//www.se.pl/lublin"):
                url = urljoin(current_url, url)
                url_components = {"url": url, "service": current_service}
                urls.add_urls(connection, url_components)
        except:
            print("NO URL")



def update_article(text, current_service, current_url, int_publication_date=20200811000):
    #articles = []
    bs = BeautifulSoup(text, "lxml")
    container = bs.find(class_="main-content")
    title = container.find("div", {"class": "title"}).h1
    print(title)
    aa_title = title.find_all(text=re.compile(r'(koronawirus|covid|epidemi|zakaże)', re.I))
    print("The count is:", len(aa_title))


    article = container.find("article")
    date_and_author_container = article.find("div", ({"class": "neck display-flex"}))

    date = date_and_author_container.find(class_="h3 pub_time_date").text
    hours = date_and_author_container.find(class_="h3 pub_time_hours_minutes").text
    publication_date = date + " " + hours
    print("STRING", publication_date)
    int_date = publication_date.replace("-", "").replace(" ", "").replace(":", "")

    if len(int_date) == 11:
        int_date = int_date[:8] + "0" + int_date[8:]
        #print(print("INT", int_date, "LEN", len(int_date)))

    if int(int_date) >= int_publication_date:
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        try:
            author = date_and_author_container.find("a").text.strip()
        except:
            author = "No author"
        if author == "No author":
            try:
                author = date_and_author_container.find_all("span")[4].text.strip()
            except:
                author = "No author"

        print(publication_date, author)
        articles.update_articles(connection, author, publication_date, current_url)


def count_words_in_title():
    pass


if __name__ == "__main__":
    services.add_services(connection, all_start_urls)
    start_urls = urls.get_start_urls(connection)
    extracted_articles = []
    next_url_counter = 0
    articels_counter = 0

    while start_urls:

        task = start_urls.pop(0)
        current_service = task["service"]
        current_url = task["start_url"]
        print(task)

        try:
            response = session.get(current_url, timeout=TIMEOUT)
            extract_urls(response.text, current_service, current_url)

        except Exception as e:
            print(e)
            continue

        try:
            pagination = BeautifulSoup(response.text, "lxml").find("ul", {"class": "horizontal paginacja"})
            link = pagination.find("li", {"class": "next"})
            link = link.find("a")
            if link:
                next_url = link.attrs.get("href")
                next_url_counter += 1
                #print("page:", next_url_counter)
                if next_url_counter == 2:
                    continue
                next_url = urljoin(current_url, next_url)
                start_urls.append({"service": current_service, "start_url": next_url})
        except Exception as e:
            print(e)
            continue

    urls = urls.get_urls(connection)
    while urls:
        task = urls.pop(0)
        current_service = task["service"]
        current_url = task["url"]
        try:

            response = session.get(current_url, timeout=TIMEOUT)
            update_article(response.text, current_service, current_url)
            articels_counter += 1
            #print("article:", articels_counter)

        except Exception as e:
            print(e)
            continue
