from mailer import Mailer
from db import DB
from scraper import Scraper

if __name__ == '__main__':
    db = DB()
    scraper = Scraper()

    # Put all new jobs into a list
    currentJobs = scraper.getAllJobs()
    oldStoredJobs = db.getAllStoredJobs()
    newJobs = []
    for currentJob in currentJobs:
        if currentJob not in oldStoredJobs:
            newJobs.append(currentJob)

    # purge the db of any job posting that have been taken down
    companiesReached = scraper.companies
    for company in companiesReached:
        db.removeMissingJobsFromCompany(currentJobs, company)

    # notify me if any new jobs are found
    if newJobs:
        mailer = Mailer()
        mailer.sendEmail(newJobs)

    db.storeNewJobs(newJobs)
