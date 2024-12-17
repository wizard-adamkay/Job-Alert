import multiprocessing
import logging
from loggingConfig import listener_process, configure_logging
from mailer import Mailer
from db import DB
from scraper import Scraper


if __name__ == '__main__':
    try:
        # Starting the logger
        logQueue = multiprocessing.Queue()
        logFile = "C:\\Users\\adamk\\Desktop\\Code\\newJobDetector\\app.log"
        listener = multiprocessing.Process(target=listener_process, args=(logQueue, logFile))
        listener.start()

        # Configure logging for the main process
        configure_logging(logQueue)
        logger = logging.getLogger(__name__)
        logger.info("Main process started")
        logger.debug("Debugging info from main process")

        db = DB()
        scraper = Scraper(logQueue)

        # Put all new jobs into a list
        currentJobs = scraper.getAllJobs()
        logger.info(f"Jobs found by scraper: {currentJobs}")
        oldStoredJobs = db.getAllStoredJobs()
        logger.info(f"Jobs that were in the db: {oldStoredJobs}")
        newJobs = []
        for currentJob in currentJobs:
            if currentJob not in oldStoredJobs:
                newJobs.append(currentJob)
        logger.info(f"Jobs identified as new: {newJobs}")

        # purge the db of any job posting that have been taken down
        companiesReached = scraper.companies
        logger.info(f"Companies included in purge: {', '.join(company.name for company in companiesReached)}")
        for company in companiesReached:
            db.removeMissingJobsFromCompany(currentJobs, company.name)

        # notify me if any new jobs are found
        if newJobs:
            mailer = Mailer()
            mailer.sendEmail(newJobs)

        db.storeNewJobs(newJobs)

        logger.info(f"final list of jobs in db: {db.getAllStoredJobs()}")
    finally:
        # Stop the logger
        logQueue.put(None)
        listener.join()
