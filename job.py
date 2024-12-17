from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    title: str
    link: str
    company: str
