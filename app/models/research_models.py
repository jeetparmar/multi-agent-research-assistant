from pydantic import BaseModel
from typing import List


class ResearchRequest(BaseModel):
    query: str


class PlanResponse(BaseModel):
    subtopics: List[str]


class ResearchResponse(BaseModel):
    query: str
    subtopics: List[str]
    report: str
