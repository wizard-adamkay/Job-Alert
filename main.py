from mailer import Mailer
from db import DB
from scraper import Scraper
import logging
from logging.handlers import RotatingFileHandler

if __name__ == '__main__':
    rotating_handler = RotatingFileHandler("app.log", maxBytes=5 * 1024 * 1024, backupCount=3)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            rotating_handler,
            logging.StreamHandler()
        ]
    )
    logging.info("Run started")
    db = DB()
    scraper = Scraper()

    # Put all new jobs into a list
    currentJobs = scraper.getAllJobs()
    logging.info(f"Jobs found by scraper: {currentJobs}")
    oldStoredJobs = db.getAllStoredJobs()
    logging.info(f"Jobs that were in the db: {oldStoredJobs}")
    newJobs = []
    for currentJob in currentJobs:
        if currentJob not in oldStoredJobs:
            newJobs.append(currentJob)
    logging.info(f"Jobs identified as new: {newJobs}")

    # purge the db of any job posting that have been taken down
    companiesReached = scraper.companies
    logging.info(f"Companies included in purge: {companiesReached}")
    for company in companiesReached:
        db.removeMissingJobsFromCompany(currentJobs, company)

    # notify me if any new jobs are found
    if newJobs:
        mailer = Mailer()
        mailer.sendEmail(newJobs)

    db.storeNewJobs(newJobs)

    logging.info(f"final list of jobs in db: {db.getAllStoredJobs()}")
