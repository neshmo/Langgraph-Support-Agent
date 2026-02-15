from pydantic import BaseModel, Field
from typing import Optional

class TicketCreate(BaseModel):
    text: str = Field(..., example="I was charged twice this month")
    ticket_id: Optional[str] = Field(None, description="Existing ticket ID for follow-ups")

class TicketProcessRequest(BaseModel):
    text: str = Field(..., min_length=1)
    
class TicketRead(BaseModel):
    ticket_id: str
    text: str
    status: str

    class Config:
        from_attributes = True
