from pydantic import BaseModel
from typing import List

# Define request and response models for the research assistant API
class ResearchRequest(BaseModel):
    query: str

# Response model for the planner agent to return subtopics
class PlanResponse(BaseModel):
    subtopics: List[str]
