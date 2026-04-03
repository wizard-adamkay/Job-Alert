import requests
import re
from multiprocessing import Queue
from job import Job
import logging
from loggingConfig import configure_logging
base_url = "https://recruiting.ultipro.ca"
mda_url = (
	f"{base_url}/MAC5000MCDW/JobBoard/664818ff-3594-4bec-9f30-3394e59e19f3/?q=&o=distance&w=Vancouver%2C+BC%2C+CAN&wc=-123.11335%2C49.261636&we=-123.27335%2C49.42163600000001%7C-122.95335%2C49.101636&wpst=2&f4=-NP_8IhlXF-fGXIRSM9fNw&f5=r6Nk37SKbUicJ3G-Ura_Tw+zbdts05UEUmmM9J30HpRfg+zhmbl8bqG02eEdHnn6_vDw"
)
page_url = f"{base_url}/MAC5000MCDW/JobBoard/664818ff-3594-4bec-9f30-3394e59e19f3/"
api_url = f"{base_url}/MAC5000MCDW/JobBoard/664818ff-3594-4bec-9f30-3394e59e19f3/JobBoardView/LoadSearchResults"
link_prepend = f"{base_url}/MAC5000MCDW/JobBoard/664818ff-3594-4bec-9f30-3394e59e19f3/OpportunityDetail?opportunityId="

headers = {
	"User-Agent": "Mozilla/5.0",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def getMDAJobs(queue: Queue, logQueue: Queue) -> None:
	configure_logging(logQueue)
	logger = logging.getLogger(__name__)
	session = requests.Session()
	page = session.get(page_url, headers=headers)
	page.raise_for_status()

	match = re.search(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"', page.text)
	if not match:
		raise RuntimeError("Could not find __RequestVerificationToken in page source")
	token = match.group(1)

	payload = {
		"opportunitySearch": {"Top": 50, "Skip": 0, "QueryString": "",
							  "OrderBy": [{"Value": "distance", "PropertyName": "Distance", "Ascending": True}],
							  "Filters": [{"t": "TermsSearchFilterDto", "fieldName": 4, "extra": None,
										   "values": ["f0ffd3f8-6588-5f5c-9f19-721148cf5f37"]},
										  {"t": "TermsSearchFilterDto", "fieldName": 5, "extra": None,
										   "values": ["df64a3af-8ab4-486d-9c27-71be52b6bf4f",
													  "b36db7cd-544e-4911-a633-d277d07a517e",
													  "979b19ce-eac6-4d1b-9e11-d1e79fafef0f"]},
										  {"t": "TermsSearchFilterDto", "fieldName": 6, "extra": None, "values": []},
										  {"t": "TermsSearchFilterDto", "fieldName": 37, "extra": None, "values": []}],
							  "Coordinates": {"Longitude": -123.11335, "Latitude": 49.261636},
							  "Extent": {"Min": {"Longitude": -123.27335, "Latitude": 49.42163600000001},
										 "Max": {"Longitude": -122.95335, "Latitude": 49.101636}},
							  "ProximitySearchType": 2},
		"matchCriteria": {"PreferredJobs": [], "Educations": [], "LicenseAndCertifications": [], "Skills": [],
						  "hasNoLicenses": False, "SkippedSkills": []}
	}

	api_headers = {
		"User-Agent": "Mozilla/5.0",
		"Accept": "application/json, text/javascript, */*; q=0.01",
		"Content-Type": "application/json; charset=utf-8",
		"Origin": base_url,
		"Referer": mda_url,
		"X-Requested-With": "XMLHttpRequest",
		"X-RequestVerificationToken": token,
	}

	response = session.post(api_url, headers=api_headers, json=payload)
	response.raise_for_status()

	data = response.json()
	for job in data["opportunities"]:
		jobId = job["Id"]
		jobTitle = job["Title"]
		queue.put(Job(jobTitle, link_prepend + jobId, "MDA Space"))
