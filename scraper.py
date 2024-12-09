import requests
import time
import logging
from lxml import html, etree
from job import Job
from requests_html import HTMLSession
from multiprocessing import Process, Queue
from companyUnreachableError import CompanyUnreachableError

imperva_url = "https://www.imperva.com/company/careers"
enea_url = "https://careers.enea.com/jobs"
treyarch_url = "https://careers.treyarch.com/search-results?keywords=vancouver"
mda_url = ("https://recruiting.ultipro.ca/MAC5000MCDW/JobBoard/664818ff-3594-4bec-9f30-3394e59e19f3/?q=&o"
		   "=postedDateDesc&w=&wc=&we=&wpst=&f4=-NP_8IhlXF-fGXIRSM9fNw&f5=zbdts05UEUmmM9J30HpRfg+r6Nk37SKbUicJ3G"
		   "-Ura_Tw")


# todo use 1 method to extract jobs from each site instead of 1 for each site
class Scraper:
	companies = ["Imperva", "Enea", "Treyarch", "MDA"]

	def getHTML(self, url):
		prevStatusCode = -1
		for count in range(5):
			response = requests.get(url)
			prevStatusCode = response.status_code
			if response.status_code == 200:
				return html.fromstring(response.content)
			time.sleep(1)
		logging.exception(f"URL: {url} responded with status code: {prevStatusCode}")
		raise CompanyUnreachableError(f"URL: {url} responded with status code: {prevStatusCode}")

	def extractJobs(self, postings, queue, company, titleXpath, linkXpath):
		logging.info(f"starting extraction for {company}")
		for posting in postings:
			try:
				title = posting.xpath(titleXpath)[0].strip()
				link = posting.xpath(linkXpath)[0]
				if company == "MDA":
					link = "https://recruiting.ultipro.ca" + link
				job = Job(title=title, link=link, company=company)
				queue.put(job)
			except IndexError as e:
				logging.exception(f"index error encountered from {company}")
				continue

	def getJobsImperva(self, queue):
		try:
			tree = self.getHTML(imperva_url)
		except CompanyUnreachableError as e:
			self.companies.remove("Imperva")
			return
		except Exception as e:
			return
		postings = tree.xpath('//li[contains(@class, "position-item") and @data-city="vancouver"]')
		titleXPath = ".//span[contains(@class, 'job-title')]/text()"
		linkXPath = "./a/@href"
		self.extractJobs(postings, queue, "Imperva", titleXPath, linkXPath)

	def getJobsEnea(self, queue):
		try:
			tree = self.getHTML(enea_url)
		except CompanyUnreachableError as e:
			self.companies.remove("Enea")
			return
		except Exception as e:
			return
		postings = tree.xpath("//span[contains(text(), 'Canada') or contains(text(), 'Vancouver')]")
		titleXPath = "../preceding-sibling::span/text()"
		linkXPath = "../../@href"
		self.extractJobs(postings, queue, "Enea", titleXPath, linkXPath)

	def getJobsTreyarch(self, queue):
		try:
			session = HTMLSession()
			r = session.get(treyarch_url)
			logging.info(f"Status code for Treyarch: {r.status_code}")
			if r.status_code != 200:
				raise CompanyUnreachableError(f"URL: {treyarch_url} responded with status code: {r.status_code}")
			r.html.render()
			tree = etree.HTML(r.html.html)
		except CompanyUnreachableError as e:
			logging.exception(f"URL: {treyarch_url} responded with status code: {r.status_code}")
			self.companies.remove("Treyarch")
			return
		except Exception as e:
			logging.exception(f"URL: {treyarch_url} had an exception")
			self.companies.remove("Treyarch")
			return
		postings = tree.xpath("//li[contains(@class, 'jobs-list-item')]")
		titleXPath = ".//div[contains(@class, 'job-title')]/span/text()"
		linkXPath = ".//div[contains(@class, 'information')]/a/@href"
		self.extractJobs(postings, queue, "Treyarch", titleXPath, linkXPath)

	def getJobsMDA(self, queue):
		try:
			session = HTMLSession()
			r = session.get(mda_url)
			logging.info(f"Status code for MDA: {r.status_code}")
			if r.status_code != 200:
				raise CompanyUnreachableError(f"URL: {mda_url} responded with status code: {r.status_code}")
			r.html.render()
			tree = etree.HTML(r.html.html)
		except CompanyUnreachableError as e:
			logging.exception(f"URL: {mda_url} responded with status code: {r.status_code}")
			self.companies.remove("MDA")
			return
		except Exception as e:
			logging.exception(f"URL: {mda_url} had an exception")
			self.companies.remove("MDA")
			return
		postings = tree.xpath("//div[contains(@class, 'opportunity')]")
		titleXPath = ".//h3/a[contains(@class, 'opportunity-link')]/text()"
		linkXPath = ".//h3/a[contains(@class, 'opportunity-link')]/@href"
		self.extractJobs(postings, queue, "MDA", titleXPath, linkXPath)

	def getAllJobs(self):
		scrapers = [self.getJobsImperva, self.getJobsEnea, self.getJobsTreyarch, self.getJobsMDA]
		queue = Queue()
		processes = []
		for scraper in scrapers:
			process = Process(target=scraper, args=(queue,))
			processes.append(process)
			process.start()
		for process in processes:
			process.join()
		results = []
		while not queue.empty():
			results.append(queue.get())
		logging.info("scraping completed")
		return results
