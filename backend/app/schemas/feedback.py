from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    ticket_id: str
    ticket_text: str
    final_response: str
    feedback: str
