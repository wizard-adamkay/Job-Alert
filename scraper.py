import requests
from lxml import html, etree
from job import Job
from requests_html import HTMLSession
from multiprocessing import Process, Queue

imperva_url = "https://www.imperva.com/company/careers"
enea_url = "https://careers.enea.com/jobs"
treyarch_url = "https://careers.treyarch.com/search-results?keywords=vancouver"


class Scraper:
	def getHTML(self, url):
		try:
			response = requests.get(url)
			response.raise_for_status()
			return html.fromstring(response.content)
		except requests.RequestException as e:
			return

	def extractJobs(self, postings, queue, company, titleXpath, linkXpath):
		for posting in postings:
			try:
				title = posting.xpath(titleXpath)[0].strip()
				link = posting.xpath(linkXpath)[0]
				job = Job(title=title, link=link, company=company)
				queue.put(job)
			except IndexError as e:
				continue

	def getJobsImperva(self, queue):
		tree = self.getHTML(imperva_url)
		postings = tree.xpath('//li[contains(@class, "position-item") and @data-city="vancouver"]')
		titleXPath = ".//span[contains(@class, 'job-title')]/text()"
		linkXPath = "./a/@href"
		self.extractJobs(postings, queue, "Imperva", titleXPath, linkXPath)

	def getJobsEnea(self, queue):
		tree = self.getHTML(enea_url)
		postings = tree.xpath("//span[contains(text(), 'Canada') or contains(text(), 'Vancouver')]")
		titleXPath = "../preceding-sibling::span/text()"
		linkXPath = "../../@href"
		self.extractJobs(postings, queue, "Enea", titleXPath, linkXPath)

	def getJobsTreyarch(self, queue):
		try:
			session = HTMLSession()
			r = session.get(treyarch_url)
			r.html.render()
			tree = etree.HTML(r.html.html)
		except Exception as e:
			return
		postings = tree.xpath("//li[contains(@class, 'jobs-list-item')]")
		titleXPath = ".//div[contains(@class, 'job-title')]/span/text()"
		linkXPath = ".//div[contains(@class, 'information')]/a/@href"
		self.extractJobs(postings, queue, "Treyarch", titleXPath, linkXPath)

	def getAllJobs(self):
		scrapers = [self.getJobsImperva, self.getJobsEnea, self.getJobsTreyarch]
		queue = Queue()
		processes = []
		for scraper in scrapers:
			process = Process(target=scraper, args=(queue, ))
			processes.append(process)
			process.start()
		for process in processes:
			process.join()
		results = []
		while not queue.empty():
			results.append(queue.get())
		return results
