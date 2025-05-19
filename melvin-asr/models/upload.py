from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str