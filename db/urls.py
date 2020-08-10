def get_start_urls(connection):
    stmt = (
        """
        SELECT service, start_url
        FROM services
        """
    )

    with connection.cursor() as cur:
        cur.execute(stmt)
        return cur.fetchall()

def get_urls(connection):
    stmt = (
        """
        SELECT S.service, U.url
        FROM services S
        JOIN urls U USING(service_id)
        """
    )

    with connection.cursor() as cur:
        cur.execute(stmt)
        return cur.fetchall()

def add_urls(connection, url_components):
    stmt = (
        """
        INSERT INTO urls(
            service_id,
            url
        )
        VALUES(
            (SELECT service_id FROM services
             WHERE service = %(service)s),
             %(url)s
        )
        ON CONFLICT (url) DO NOTHING
        RETURNING *
        """
    )
    with connection.cursor() as cur:
        record = {"service": url_components["service"],
                  "url": url_components["url"]}
        cur.execute(stmt, record)
        cur.connection.commit()
        return cur.fetchall()