# nlp_se_koronawirus


Step 1:
Create a database. In the terminal, enter the command: "make initdb". The command will delete the database if it exists,
then create a new database and create the database schema.

Step 2:
Open the "scraping/start_urls.py" file and see which local sites will be checked.

Step 3:
Run the file "scraping / scraping.py" and download the data from the website. The data will be saved in the postgres
database. Set the end update date for the articles (upgrade_article (end_date)). By default, the date is set to 2020.01.01

Step 4: