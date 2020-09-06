# nlp_se_koronawirus


**Step 1:**
Create a database. In the terminal, enter the command: "make initdb". The command will delete the database if it exists,
then create a new database and create the database schema.

**Step 2:**
Open the "scraping/start_urls.py" file and see which local sites will be checked.

**Step 3:**
Run the file "scraping/scraping.py" and download the data from the website. The data will be saved in the postgres
database. Set the end update date for the articles (upgrade_article (end_date)). By default, the date is set to 2020.01.01

**Step 4:**
Run the Jupyter Notebook file "data_cleaning.ipynb". Get data from database. Clean data and save to 
"datasets/1_clean_data.csv" file.

**Step 5:**
Run the Jupyter Notebook file "data_analysis_and_visualization.ipynb". You will get the data:
- First articles with covid in the title, 
- Number of articles with covid in the title, 
- Mean number of covid articles in the title,
- Number of articles with covid in the title each month,
- Number of articles with covid in the text,
- Number of covid articles in the text each month,
- Articles from July and August with covid in the title / without covid in the text,
- Total number of articles in the text each month,
- Total number of articles,
- Days with a record number of articles,
- Covid article count per 100 articles,
- The total number of covid words,
- Mean covid word count per article,
- Articles with the highest number of words in the covid group,
- Total covid words each month,
- Total covid words each month without top 3,
- Covid article without top 3 count per 1000 articles,
- The author of the largest number of articles with the word from the covid group in the title,
- The author of the largest number of articles with the word from the covid group in the text,
- The author of the largest number of articles with the word from the covid - total covid words each month,
- The author of the largest number of articles with the word from the covid - total covid articles,
- The author of the largest number of articles with the word from the covid - total covid articles each month,
- The total number of words in all articles,
- The article with the most words,
- Question mark and exclamation mark sum



