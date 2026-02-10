from pydantic import BaseModel, Field
from typing import Optional

class ProjectEntity(BaseModel):
    title: str
    url: Optional[str] = None
    description: str = Field(..., description="Snippet or full text description")

class ServiceEntity(BaseModel):
    name: str = Field(..., alias="service")
    price: float
    description: Optional[str] = None
