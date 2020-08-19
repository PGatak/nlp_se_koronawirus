def update_articles(connection, author, publication_date, current_url, koronawirus_in_title, text_title,
                    covid_word_counter, all_word_counter, question_mark_counter, exclamation_mark_counter):
    stmt = (
        """
        UPDATE urls
        SET author = %(author)s,
            publication_date = %(publication_date)s,
            koronawirus_in_title = %(koronawirus_in_title)s,
            koronawirus_in_text = %(covid_word_counter)s,
            title = %(text_title)s,
            all_words = %(all_word_counter),
            question_mark = %(question_mark_counter),
            exclamation_mark = %(exclamation_mark_counter)
        WHERE url = %(current_url)s
        """
    )
    with connection.cursor() as cur:
        record = {"author": author,
                  "publication_date": publication_date,
                  "current_url": current_url,
                  "koronawirus_in_title": koronawirus_in_title,
                  "covid_word_counter": covid_word_counter,
                  "text_title": text_title,
                  "all_word_counter": all_word_counter,
                  "question_mark_counter": question_mark_counter,
                  "exclamation_mark_counter": exclamation_mark_counter}
        cur.execute(stmt, record)
        cur.connection.commit()
        return cur.fetchall()


def get_articles_grouped_by_date(connection, starting_date, end_date):
    stmt = (
        """
        SELECT url
        FROM urls
        WHERE created_on > %(starting_date)s AND created_on < %(end_date)s
        """
    )

    with connection.cursor() as cur:
        record = {"starting_date": starting_date,
                  "end_date": end_date}
        cur.execute(stmt, dict(starting_date=starting_date, end_date=end_date))
        #cur.connection.commit()
        return cur.fetchall()


def get_articles_grouped_by_author(connection, name):
    stmt = (
        """
        SELECT url
        FROM urls
        WHERE author = %(name)s
        """
    )

    with connection.cursor() as cur:
        cur.execute(stmt, dict(name=name))
        #cur.connection.commit()
        return cur.fetchall()

def get_articles(connection):
    stmt = (
        """
        SELECT *
        FROM urls
        """
    )

    with connection.cursor() as cur:
        cur.execute(stmt)
        return cur.fetchall()
