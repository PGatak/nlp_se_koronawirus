def update_articles(connection, article):
    stmt = (
        """
        UPDATE urls
        SET author = %(author)s,
            publication_date = %(publication_date)s,
            koronawirus_in_title = %(koronawirus_in_title)s,
            koronawirus_in_text = %(covid_word_counter)s,
            title = %(text_title)s,
            all_words = %(all_word_counter)s,
            question_mark = %(question_mark_counter)s,
            exclamation_mark = %(exclamation_mark_counter)s
        WHERE url = %(url)s
        """
    )
    with connection.cursor() as cur:
        cur.execute(stmt, article.__dict__)
        cur.connection.commit()
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