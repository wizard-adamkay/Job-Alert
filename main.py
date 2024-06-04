from mailer import Mailer
from db import DB
from scraper import Scraper

if __name__ == '__main__':
    db = DB()
    scraper = Scraper()
    currentJobs = scraper.getAllJobs()
    storedJobs = db.getStoredJobs()
    newJobs = []
    for job in currentJobs:
        if job not in storedJobs:
            newJobs.append(job)
    if newJobs:
        mailer = Mailer()
        mailer.sendEmail(newJobs)
    db.overwriteDB(currentJobs)
    db.storeNewJobs(newJobs)
