CREATE TABLE services(
    service_id SERIAL PRIMARY KEY,
    service TEXT UNIQUE,
    start_url TEXT,
    created_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE urls(
    url_id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(service_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
    author TEXT,
    publication_date TIMESTAMP,
    url TEXT UNIQUE,
    title TEXT,
    koronawirus_in_text SMALLINT,
    koronawirus_in_title SMALLINT,
    all_words SMALLINT,
    question_mark SMALLINT,
    exclamation_mark SMALLINT,
    created_on TIMESTAMP DEFAULT NOW()
);