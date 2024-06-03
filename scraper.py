import requests
from lxml import html
from job import Job

imperva_url = "https://www.imperva.com/company/careers"
enea_url = "https://careers.enea.com/jobs"


class Scraper:
	def getJobsImperva(self):
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

	def getJobsEnea(self):
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

	def getAllJobs(self):
		jobs = self.getJobsImperva()
		jobs += self.getJobsEnea()
		return jobs
