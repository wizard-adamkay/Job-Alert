import sqlite3
from job import Job

db_name = "C:\\Users\\adamk\\Desktop\\Code\\newJobDetector\\jobs.db"


class DB:
	def __init__(self):
		with sqlite3.connect(db_name) as conn:
			c = conn.cursor()
			c.execute('''CREATE TABLE IF NOT EXISTS jobs
		                         (id INTEGER PRIMARY KEY, title TEXT, link TEXT, company TEXT)''')
			conn.commit()

	def getAllStoredJobs(self):
		conn = sqlite3.connect(db_name)
		c = conn.cursor()
		c.execute("SELECT title, link, company FROM jobs")
		storedJobs = set(Job(title=row[0], link=row[1], company=row[2]) for row in c.fetchall())
		conn.close()
		return storedJobs

	def getStoredJobsByCompany(self, company, conn=None):
		closeConn = False
		if conn is None:
			closeConn = True
			conn = sqlite3.connect(db_name)
		c = conn.cursor()
		c.execute("SELECT title, link, company FROM jobs WHERE company = ?", (company,))
		storedJobs = [Job(title=row[0], link=row[1], company=row[2]) for row in c.fetchall()]
		if closeConn:
			conn.close()
		return storedJobs

	def storeNewJobs(self, new_jobs):
		with sqlite3.connect(db_name) as conn:
			c = conn.cursor()
			for job in new_jobs:
				c.execute("INSERT INTO jobs (title, link, company) VALUES (?, ?, ?)",
						  (job.title, job.link, job.company))
			conn.commit()

	# removes any job that is no longer posted by the company from the db
	def removeMissingJobsFromCompany(self, currentJobs, company):
		with sqlite3.connect(db_name) as conn:
			c = conn.cursor()
			jobsInDB = self.getStoredJobsByCompany(company, conn)
			# if the job has been taken down from the site, remove it from db
			for jobInDB in jobsInDB:
				if jobInDB not in currentJobs:
					c.execute("DELETE FROM jobs WHERE title = ? AND link = ? AND company = ?",
							  (jobInDB.title, jobInDB.link, jobInDB.company))
			conn.commit()
