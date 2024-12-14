import requests
import time
import logging
from lxml import html, etree
from company import Company
from job import Job
from requests_html import HTMLSession
from multiprocessing import Process, Queue
from companyUnreachableError import CompanyUnreachableError
from loggingConfig import configure_logging

imperva_url = "https://www.imperva.com/company/careers"
enea_url = "https://careers.enea.com/jobs"
treyarch_url = "https://careers.treyarch.com/search-results?keywords=vancouver"
mda_url = (
	"https://recruiting.ultipro.ca/MAC5000MCDW/JobBoard/664818ff-3594-4bec-9f30-3394e59e19f3/?q=&o"
	"=postedDateDesc&w=&wc=&we=&wpst=&f4=-NP_8IhlXF-fGXIRSM9fNw&f5=zbdts05UEUmmM9J30HpRfg+r6Nk37SKbUicJ3G"
	"-Ura_Tw"
)


class Scraper:
	companies = [
		Company(
			"Imperva", imperva_url, '//li[contains(@class, "position-item") and @data-city="vancouver"]',
			".//span[contains(@class, 'job-title')]/text()", "./a/@href"
		),
		Company(
			"Enea", enea_url, "//span[contains(text(), 'Canada') or contains(text(), 'Vancouver')]",
			"../preceding-sibling::span/text()", "../../@href"
		),
		Company(
			"Treyarch", treyarch_url, "//li[contains(@class, 'jobs-list-item')]",
			".//div[contains(@class, 'job-title')]/span/text()",
			".//div[contains(@class, 'information')]/a/@href",
			type="session"
		),
		Company(
			"MDA", mda_url, "//div[contains(@class, 'opportunity')]",
			".//h3/a[contains(@class, 'opportunity-link')]/text()",
			".//h3/a[contains(@class, 'opportunity-link')]/@href",
			type="session", linkPrepend="https://recruiting.ultipro.ca"
		)
	]

	def __init__(self, logQueue):
		self.logQueue = logQueue

	def getHTML(self, url, logger):
		prevStatusCode = -1
		for count in range(5):
			response = requests.get(url)
			prevStatusCode = response.status_code
			if response.status_code == 200:
				return html.fromstring(response.content)
			time.sleep(1)
		logger.exception(f"URL: {url} responded with status code: {prevStatusCode}")
		raise CompanyUnreachableError(f"URL: {url} responded with status code: {prevStatusCode}")

	def extractJobs(self, tree, queue, company, logger):
		logger.info(f"starting extraction for {company.name}")
		postings = tree.xpath(company.postingsXPath)
		for posting in postings:
			try:
				title = posting.xpath(company.titleXPath)[0].strip()
				link = posting.xpath(company.linkXPath)[0]
				link = company.linkPrepend + link
				job = Job(title=title, link=link, company=company.name)
				queue.put(job)
			except IndexError as e:
				logger.exception(f"index error encountered from {company}")
				logger.exception(posting)
				continue

	def getJobs(self, queue, company, logQueue):
		configure_logging(logQueue)
		logger = logging.getLogger(__name__)
		try:
			tree = self.getHTML(company.link, logger)
		except CompanyUnreachableError as e:
			self.companies.remove(company)
			return
		except Exception as e:
			logger.exception(f"URL: {company.link} had an exception")
			self.companies.remove(company)
			return
		self.extractJobs(tree, queue, company, logger)

	def getJobsSession(self, queue, company, logQueue):
		configure_logging(logQueue)
		logger = logging.getLogger(__name__)
		try:
			session = HTMLSession()
			r = session.get(company.link)
			logging.info(f"Status code for {company.name}: {r.status_code}")
			if r.status_code != 200:
				raise CompanyUnreachableError(f"URL: {company.link} responded with status code: {r.status_code}")
			r.html.render()
			tree = etree.HTML(r.html.html)
		except CompanyUnreachableError as e:
			logging.exception(f"URL: {company.link} responded with status code: {r.status_code}")
			self.companies.remove(company)
			return
		except Exception as e:
			logging.exception(f"URL: {company.link} had an exception")
			self.companies.remove(company)
			return
		self.extractJobs(tree, queue, company, logger)

	def getAllJobs(self):
		queue = Queue()
		processes = []
		for company in self.companies:
			target = self.getJobsSession if company.type == "session" else self.getJobs
			process = Process(target=target, args=(queue, company, self.logQueue))
			processes.append(process)
			process.start()
		for process in processes:
			process.join()
		results = []
		while not queue.empty():
			results.append(queue.get())
		logging.info("scraping completed")
		return results
