.PHONY: all

DBNAME		?= nlp_se_koronawisus_sql


initdb:
	dropdb --if-exists $(DBNAME)
	createdb $(DBNAME)
	psql -1 $(DBNAME) < sql/schema.sql