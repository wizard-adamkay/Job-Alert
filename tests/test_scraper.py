import unittest
from unittest.mock import patch, MagicMock
from scraper import Scraper
from job import Job
from lxml import html
from company import Company
from multiprocessing import Queue
from companyUnreachableError import CompanyUnreachableError


class ScraperTests(unittest.TestCase):
	def setUp(self):
		self.log_queue = Queue()
		self.scraper = Scraper(self.log_queue)
		self.company1 = Company(
			name="Test Company",
			link="http://example.com/jobs",
			postingsXPath="//job",
			titleXPath="./title/text()",
			linkXPath="./@href",
			type="simple",
			linkPrepend="http://example.com"
		)
		self.company2 = Company(
			name="Test Company",
			link="http://example.com/jobs",
			postingsXPath="//job",
			titleXPath="./title/text()",
			linkXPath="./@href",
			type="session",
			linkPrepend="http://example.com"
		)

	@patch("scraper.requests.get")
	def test_getHTML_WhenWebsiteRespondsWith200_ReturnExpectedHTML(self, mock_get):
		mock_get.return_value.status_code = 200
		mock_get.return_value.content = b"<html><body><job><title>Test Job</title><link>/job/1</link></job></body></html>"
		logger = MagicMock()

		tree = self.scraper.getHTML("http://example.com", logger)
		self.assertIsNotNone(tree)
		self.assertEqual(tree.xpath("//job/title/text()")[0], "Test Job")

	@patch("scraper.requests.get")
	def test_getHTML_WhenWebsiteRespondsWith404_RaiseCompanyUnreachableError(self, mock_get):
		mock_get.return_value.status_code = 404
		logger = MagicMock()

		with self.assertRaises(CompanyUnreachableError):
			self.scraper.getHTML("http://example.com", logger)

		logger.exception.assert_called_with("URL: http://example.com responded with status code: 404")

	def test_extractJobs_success(self):
		logger = MagicMock()
		html_content = """
	     <html>
	         <body>
	             <job href="/job/1">
	                 <title>Job Title 1</title>
	             </job>
	             <job href="/job/2">
	                 <title>Job Title 2</title>
	             </job>
	         </body>
	     </html>
	     """
		tree = html.fromstring(html_content)
		queue = Queue()

		self.scraper.extractJobs(tree, queue, self.company1, logger)

		self.assertFalse(queue.empty(), "Queue should not be empty after extracting jobs.")
		jobs = []
		while not queue.empty():
			jobs.append(queue.get())

		self.assertEqual(len(jobs), 2, "Should only have two jobs in queue.")
		self.assertEqual(jobs[0].title, "Job Title 1", "First job title should match.")
		self.assertEqual(jobs[0].link, "http://example.com/job/1", "First job link should match.")
		self.assertEqual(jobs[1].title, "Job Title 2", "Second job title should match.")
		self.assertEqual(jobs[1].link, "http://example.com/job/2", "Second job link should match.")

	def test_extractJobs_no_postings(self):
		logger = MagicMock()

		html_content = "<html><body></body></html>"
		tree = html.fromstring(html_content)
		queue = Queue()

		self.scraper.extractJobs(tree, queue, self.company1, logger)

		self.assertTrue(queue.empty(), "Queue should be empty when no postings are found.")

	@patch("scraper.HTMLSession")
	def test_getJobsSession_success(self, mock_session):
		mock_instance = mock_session.return_value
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.html.html = """
		    <html>
		        <body>
		            <job href="/job/1">
		                <title>Test Job</title>
		            </job>
		        </body>
		    </html>
		    """
		mock_response.html.render = MagicMock()
		mock_instance.get.return_value = mock_response

		queue = Queue()
		self.scraper.getJobsSession(queue, self.company1, self.log_queue)

		self.assertFalse(queue.empty(), "Queue should not be empty after scraping.")
		job = queue.get()
		self.assertEqual(job.title, "Test Job", "Job title should match the scraped title.")
		self.assertEqual(job.link, "http://example.com/job/1", "Job link should match.")

	@patch("scraper.Queue")
	@patch("scraper.Process")
	def test_getAllJobs(self, mock_process, mock_queue):
		mock_queue_instance = MagicMock()
		# first two calls to empty should return false to mimic a non-empty queue
		mock_queue_instance.empty.side_effect = [False, False, True]
		mock_queue_instance.get.side_effect = [
			Job("Test Job", "http://example.com/job/1", "Test Company"),
			Job("Another Job", "http://example.com/job/2", "Test Company"),
		]
		mock_queue.return_value = mock_queue_instance
		# replace start and join methods with nothing to prevent new processes
		mock_process.return_value = MagicMock(start=MagicMock(), join=MagicMock())

		results = self.scraper.getAllJobs()

		self.assertEqual(len(results), 2)
		self.assertIn(Job("Test Job", "http://example.com/job/1", "Test Company"), results)
		self.assertIn(Job("Another Job", "http://example.com/job/2", "Test Company"), results)


if __name__ == '__main__':
	unittest.main()
