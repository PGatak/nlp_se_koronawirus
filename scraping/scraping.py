from bs4 import BeautifulSoup
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

connection = create_connection()


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
        elif domain == "www.se.pl" and parsed.path == "/lublin":
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
    try:
        article.find("p", {"class": "playerBoard__text playerBoard__text--icon"}).decompose()
    except:
        print("NO CLASS: playerBoard__text playerBoard__text--icon")

    try:
        article.find("p", {"class": "playerBoard__text playerBoard__title"}).decompose()
    except:
        print("NO CLASS: playerBoard__text playerBoard__title")

    try:
        article.find("p", {"class": "playerBoard__text"}).decompose()
    except:
        print("NO CLASS: playerBoard__text")

    return article


def update_article(text, current_url, end_date=202001010000):
    bs = BeautifulSoup(text, "lxml")
    container = bs.find(class_="main-content")
    article = container.find("article")

    dismiss_the_ad_paragraphs(article)

    date_and_author_container = article.find("div", ({"class": "neck display-flex"}))
    date = date_and_author_container.find(class_="h3 pub_time_date").text
    hours = date_and_author_container.find(class_="h3 pub_time_hours_minutes").text
    publication_date = date + " " + hours
    int_date = publication_date.replace("-", "").replace(" ", "").replace(":", "")

    if len(int_date) == 11:
        int_date = int_date[:8] + "0" + int_date[8:]

    if int(int_date) < end_date:
        print("Incorrect date: %s" % date)

    elif int(int_date) >= end_date:
        title = container.find("div", {"class": "title"}).h1
        text_title = title.text
        covid_regex_pattern = re.compile(r"(koronawirus|covid|epidemi|zakaże|pandemi|kwarantann|ozdrowieńc|zarazi|"
                                         r"obostrze|żółta strefa|czerwona strefa|zakażon|zaraże|odkaża|zakażn|"
                                         r"masecz(ka|ki|ek|kami)? ochronn(a|e|ych|ymi)|"
                                         r"mas(ka|ki|ek|kami)? ochronn(a|e|ych|ymi)|"
                                         r"rękawiczk(a|i|ami)? ochronn(a|e|ymi)|"
                                         r"dezynfek|sars)", re.I)

        covid_regex = title.find_all(text=covid_regex_pattern)
        koronawirus_in_title = len(covid_regex)

        text = article.find_all("p")

        article_text = []

        question_mark_regex_pattern = re.compile(r'.*\?.*')
        exclamation_mark_regex_pattern = re.compile(r'.*!.*')

        for item in text:
            article_text.append(item.text)

        words_list = list_into_words(article_text)

        covid_word_counter = 0
        all_word_counter = 0
        question_mark_counter = 0
        exclamation_mark_counter = 0
        for word in words_list:
            if covid_regex_pattern.search(word):
                covid_word_counter += 1
            if question_mark_regex_pattern.search(word):
                question_mark_counter += 1
            if exclamation_mark_regex_pattern.search(word):
                exclamation_mark_counter += 1

            all_word_counter += 1

            if word in string.punctuation:
                all_word_counter -= 1

        print(f"{date},"
              f"{text_title[:60]},"
              f"covid in title: {koronawirus_in_title},"
              f"covid word counter: {covid_word_counter},"
              f"all words: {all_word_counter},"
              f"question mark: {question_mark_counter},"
              f"exclamation mark: {exclamation_mark_counter}")

        try:
            author = date_and_author_container.find("a").text.strip()

        except:
            try:
                author = date_and_author_container.find_all("span")[4].text.strip()
            except:
                author = "No author"

        articles_api.update_articles(connection, author, publication_date, current_url, koronawirus_in_title, text_title,
                                 covid_word_counter, all_word_counter, question_mark_counter, exclamation_mark_counter)


if __name__ == "__main__":
    services_api.add_services(connection, all_start_urls)
    start_urls = urls_api.get_start_urls(connection)
    extracted_articles = []
    next_url_counter = 0

    while start_urls:
        task = start_urls.pop(0)
        current_service = task["service"]
        current_url = task["start_url"]

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
                print("%s page: %s" % (current_service, next_url_counter))
                if next_url_counter == 2:
                    continue

                next_url = urljoin(current_url, next_url)
                start_urls.append({"service": current_service, "start_url": next_url})
        except Exception as e:
            print(e)
            continue

    urls = urls_api.get_urls(connection)

    while urls:
        task = urls.pop(0)
        current_service = task["service"]
        current_url = task["url"]

        try:
            response = session.get(current_url, timeout=TIMEOUT)
            update_article(response.text, current_url)

        except Exception as e:
            print(e)
            continue
