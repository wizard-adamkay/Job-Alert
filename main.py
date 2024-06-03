import requests
from lxml import html

from job import Job
from mailer import Mailer
from db import DB

imperva_url = "https://www.imperva.com/company/careers"
enea_url = "https://careers.enea.com/jobs"
def getJobsImperva():
    r = requests.get(imperva_url)
    tree = html.fromstring(r.content)
    li = tree.xpath('//li[contains(@class, "position-item") and @data-city="vancouver"]')
    jobs = []
    for posting in li:
        try:
            title = posting.xpath(".//span[contains(@class, 'job-title')]/text()")[0]
            link = posting.xpath("./a/@href")[0]
            jobs.append(Job(title=title, link=link, company="Imperva"))
        except IndexError:
            continue
    return jobs

def getJobsEnea():
    r = requests.get(enea_url)
    tree = html.fromstring(r.content)
    spans = tree.xpath("//span[contains(text(), 'Canada') or contains(text(), 'Vancouver')]")
    jobs = []
    for span in spans:
        try:
            title = span.xpath("../preceding-sibling::span/text()")[0]
            link = span.xpath("../../@href")[0]
            company = "Enea"
            jobs.append(Job(title=title, link=link, company=company))
        except IndexError:
            continue
    return jobs


if __name__ == '__main__':
    db = DB()
    currentJobs = getJobsImperva()
    currentJobs += getJobsEnea()
    storedJobs = db.getStoredJobs()
    newJobs = []
    for job in currentJobs:
        if job not in storedJobs:
            print(f"{job} is a new job!!")
            newJobs.append(job)
    if newJobs:
        mailer = Mailer()
        mailer.sendEmail(newJobs)
    db.overwriteDB(currentJobs)
    db.storeNewJobs(newJobs)
