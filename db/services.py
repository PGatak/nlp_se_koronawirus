def add_services(connection, all_start_urls):
    stmt = (
        """
        INSERT INTO services(
            service,
            start_url
        )
        VALUES(
            %(service)s,
            %(start_url)s
        )
        ON CONFLICT (service) DO NOTHING
        RETURNING *
        """
    )
    with connection.cursor() as cur:
        for service, start_url in all_start_urls.items():
            record = {"service": service,
                      "start_url": start_url}
            cur.execute(stmt, record)
        cur.connection.commit()
        return cur.fetchall()
