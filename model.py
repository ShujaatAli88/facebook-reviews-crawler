from pydantic import BaseModel

class Review(BaseModel):
    user_id: str
    review_by: str
    comment: str