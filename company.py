from job import Job


class Company:
    def __init__(self, name, link, postingsXPath, titleXPath, linkXPath, type="simple", linkPrepend=""):
        self.name = name
        self.link = link
        self.postingsXPath = postingsXPath
        self.titleXPath = titleXPath
        self.linkXPath = linkXPath
        self.type = type  # make this an enum later
        self.linkPrepend = linkPrepend
