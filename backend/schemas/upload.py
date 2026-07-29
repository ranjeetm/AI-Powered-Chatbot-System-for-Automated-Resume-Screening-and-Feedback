from pydantic import BaseModel


# --------------------------------
# UPLOAD RESPONSE
# --------------------------------

class UploadResumeResponse(BaseModel):

    message: str

    file_name: str


class CandidateApplyResponse(BaseModel):

    message: str

    file_name: str

    candidate_name: str

    email: str
