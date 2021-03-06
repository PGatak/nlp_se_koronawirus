from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import re
import requests
import string
from urllib.parse import urljoin, urlparse
from db import (
    create_connection,
    articles as articles_api,
    services as services_api,
    urls as urls_api
)
from start_urls import all_start_urls

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
)
session = requests.Session()
session.headers.update({"User-agent": UA})
TIMEOUT = 60
COVID_REGEX_PATTERN = re.compile(
    r"(koronawirus|covid|epidemi|zakaże|pandemi|kwarantann|ozdrowieńc|zarazi|"
    r"obostrze|żółta strefa|czerwona strefa|zakażon|zaraże|odkaża|zakażn|"
    r"masecz(ka|ki|ek|kami)? ochronn(a|e|ych|ymi)|"
    r"mas(ka|ki|ek|kami)? ochronn(a|e|ych|ymi)|"
    r"rękawiczk(a|i|ami)? ochronn(a|e|ymi)|"
    r"dezynfek|sars)", re.I
)

connection = create_connection()


class Article:
    def __init__(self,
                 author=None,
                 publication_date=None,
                 url=None,
                 koronawirus_in_title=None,
                 text_title=None,
                 covid_word_counter=None,
                 all_word_counter=None,
                 question_mark_counter=None,
                 exclamation_mark_counter=None):
        self.author = author
        self.publication_date = publication_date
        self.url = url
        self.koronawirus_in_title = koronawirus_in_title
        self.text_title = text_title
        self.covid_word_counter = covid_word_counter
        self.all_word_counter = all_word_counter
        self.question_mark_counter = question_mark_counter
        self.exclamation_mark_counter = exclamation_mark_counter


def extract_urls(text, current_service, current_url):
    bs = BeautifulSoup(text, "lxml")
    container = bs.find(class_="gl_plugin listing")
    items = container.find_all("a")
    for item in items:
        url = item.attrs.get("href", "")
        parsed = urlparse(url)
        (domain, *port) = parsed.netloc.split(":")
        domain = domain.lower()
        if domain == "lublin.se.pl":
            url = urljoin(current_url, url)
            url_components = {"url": url, "service": current_service}
            urls_api.add_urls(connection, url_components)
        elif url.startswith("//www.se.pl/lublin"):
            url = urljoin(current_url, url)
            url_components = {"url": url, "service": current_service}
            urls_api.add_urls(connection, url_components)


def list_into_words(article_text: list):
    article_string_text = ",".join(article_text)
    article_list_text = article_string_text.split(",")
    article_string_text = ".".join(article_list_text)
    article_list_text = article_string_text.split(".")
    article_string_text = "".join(article_list_text)
    article_list_text = article_string_text.split()

    return article_list_text


def dismiss_the_ad_paragraphs(article):
    css_classes = [
        "playerBoard__text playerBoard__text--icon",
        "playerBoard__text playerBoard__title",
        "playerBoard__text",
    ]
    try:
        [article.find("p", {"class": cls}).decompose() for cls in css_classes]
    except AttributeError as e:
        print("NO CLASS:", e)
    return article


def parse_article(text, current_url, end_date=datetime(2020, 1, 1)):
    bs = BeautifulSoup(text, "lxml")
    container = bs.find(class_="main-content")
    article = container.find("article")

    dismiss_the_ad_paragraphs(article)

    date_and_author = article.find(
        "div",
        {"class": "neck display-flex"}
    )
    publication_date = date_and_author.find(class_="h3 pub_time_date").text
    publication_date = datetime.strptime(publication_date, "%Y-%m-%d")

    if publication_date < end_date:
        print(f"Incorrect date: {publication_date}")

    elif publication_date >= end_date:
        title = container.find("div", {"class": "title"}).h1
        text_title = title.text

        covid_regex = title.find_all(text=COVID_REGEX_PATTERN)
        koronawirus_in_title = len(covid_regex)

        text = article.find_all("p")

        article_text = []

        for item in text:
            article_text.append(item.text)

        words_list = list_into_words(article_text)

        covid_word_counter = 0
        all_word_counter = 0
        question_mark_counter = 0
        exclamation_mark_counter = 0
        for word in words_list:
            if COVID_REGEX_PATTERN.search(word):
                covid_word_counter += 1
            if "?" in word:
                question_mark_counter += 1
            if "!" in word:
                exclamation_mark_counter += 1

            all_word_counter += 1

            if word in string.punctuation:
                all_word_counter -= 1

        print(f"{publication_date},"
              f"{text_title[:60]},"
              f"covid in title: {koronawirus_in_title},"
              f"covid word counter: {covid_word_counter},"
              f"all words: {all_word_counter},"
              f"question mark: {question_mark_counter},"
              f"exclamation mark: {exclamation_mark_counter}")

        author = (
            date_and_author.find("a")
            or date_and_author.find_all("span")[4])
        author = author.text.strip() if author else "No author"

        article_object = Article(
            author=author,
            publication_date=publication_date,
            url=current_url,
            koronawirus_in_title=koronawirus_in_title,
            text_title=text_title,
            covid_word_counter=covid_word_counter,
            all_word_counter=all_word_counter,
            question_mark_counter=question_mark_counter,
            exclamation_mark_counter=exclamation_mark_counter,
        )

        return article_object


def update_article(connection, article):
    articles_api.update_articles(
        connection,
        article
    )


if __name__ == "__main__":
    services_api.add_services(connection, all_start_urls)
    start_urls = urls_api.get_start_urls(connection)
    extracted_articles = []
    next_url_counter = 0

    while start_urls:
        task = start_urls.pop(0)
        current_service = task["service"]
        current_url = task["start_url"]
        response = None

        try:
            response = session.get(current_url, timeout=TIMEOUT)
        except requests.exceptions.RequestException as e:
            print(e)
            continue
        if not response.ok:
            continue

        try:
            extract_urls(response.text, current_service, current_url)
            soup = BeautifulSoup(response.text, "lxml")
            pagination = soup.find("ul", {"class": "horizontal paginacja"})
            link = pagination.find("li", {"class": "next"})
            link = link.find("a")
            if link:
                next_url = link.attrs.get("href")
                next_url_counter += 1
                print(f"{current_service} page: {next_url_counter}")

                next_url = urljoin(current_url, next_url)
                start_urls.append({"service": current_service,
                                   "start_url": next_url})
        except Exception as e:
            # catching all exceptions to continue anyway
            print(e)
            continue

    urls = urls_api.get_urls(connection)

    while urls:
        task = urls.pop(0)
        current_service = task["service"]
        current_url = task["url"]
        response = None

        try:
            response = session.get(current_url, timeout=TIMEOUT)
            article = parse_article(response.text, current_url)
            if article:
                update_article(connection, article)
        except (requests.exceptions.RequestException,
                psycopg2.DatabaseError) as e:
            print("SKIP", e)
            continue
        except Exception as e:
            print("ERROR", e)
