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

	def getStoredJobs(self, conn=None):
		closeConn = False
		if conn is None:
			closeConn = True
			conn = sqlite3.connect(db_name)
		c = conn.cursor()
		c.execute("SELECT title, link, company FROM jobs")
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

	def overwriteDB(self, currentJobs):
		with sqlite3.connect(db_name) as conn:
			c = conn.cursor()
			oldJobs = self.getStoredJobs(conn)
			for job in oldJobs:
				if job not in currentJobs:
					c.execute("DELETE FROM jobs WHERE title = ? AND link = ? AND company = ?",
							  (job.title, job.link, job.company))
			conn.commit()
