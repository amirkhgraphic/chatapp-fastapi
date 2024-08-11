from datetime import datetime

from pydantic import BaseModel


class MyBaseModel(BaseModel):
    created_at: datetime = datetime.now()
