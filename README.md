# Job Alert Application
Custom job alerts for companies that don't have a job alert function. Email's alerts to specified gmail address.

## How to run:

1. Download the most recent version.
2. Change the db_name variable within db.py to wherever you want the db to be made.
3. Set environment variables BOTEMAIL and MYEMAIL to their respective email addresses.
4. Execute keyring.set_password("email_service", (bot gmail here), (bot gmail's access code))
5. (optional) Swap the city and country within scraper.py to preferred job search location.
6. run the command "pip install -r requirements.txt"
7. Run using the command python3 main.py
8. (optional) Set a Cron job or task scheduler to run hourly.

## How It's Made:

**Tech used:** Python, Requests, lxml, SQLite

The Job Alert application operates by scraping the career page's of specified companies. Any job postings found within the specified city will be compared against an SQLite database to check if it is a new posting. The new postings are then sent via gmail to the specified gmail address. If any postings are missing from the career page, they will also be removed from the database.

## Lessons Learned:

1. Email Automation: Automating email alerts with Python and Gmail taught me about email protocols, security practices, and managing credentials securely using environment variables and keyring.

2. Task Scheduling: Setting up task schedulers for the periodic script execution provided insights into the importance of time management and system resource optimization to ensure the application runs efficiently.

3. Configuration Complexity: The current setup process is cumbersome and highlighted the necessity of creating more user-friendly configuration procedures. Simplifying this aspect will be a key focus in future iterations to improve user experience.
