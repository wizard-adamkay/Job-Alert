import requests
from lxml import html, etree
from job import Job
from requests_html import HTMLSession

imperva_url = "https://www.imperva.com/company/careers"
enea_url = "https://careers.enea.com/jobs"
treyarch_url = "https://careers.treyarch.com/search-results?keywords=vancouver"


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

	def getJobsTreyarch(self):
		session = HTMLSession()
		r = session.get(treyarch_url)
		r.html.render()
		html_content = r.html.html
		parser = etree.HTMLParser()
		tree = etree.fromstring(html_content, parser)
		lis = tree.xpath("//li[contains(@class, 'jobs-list-item')]")
		jobs = []
		for li in lis:
			try:
				link = li.xpath(".//div[contains(@class, 'information')]/a/@href")[0]
				title = li.xpath(".//div[contains(@class, 'job-title')]/span/text()")[0]
				company = "Treyarch"
				jobs.append(Job(title=title, link=link, company=company))
			except IndexError:
				continue
		return jobs

	def getAllJobs(self):
		jobs = self.getJobsImperva()
		jobs += self.getJobsEnea()
		jobs += self.getJobsTreyarch()
		return jobs
