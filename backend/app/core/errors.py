from fastapi import HTTPException, status

class PaperFlowException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class JobNotFoundException(PaperFlowException):
    def __init__(self, job_id: str):
        super().__init__(f"Job '{job_id}' not found or has expired.", status.HTTP_404_NOT_FOUND)

class InvalidFileException(PaperFlowException):
    def __init__(self, detail: str):
        super().__init__(f"File validation failed: {detail}", 422)

class ProcessingException(PaperFlowException):
    def __init__(self, detail: str):
        super().__init__(f"Document processing failed: {detail}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnsupportedOperationException(PaperFlowException):
    def __init__(self, detail: str):
        super().__init__(f"Operation not supported: {detail}", status.HTTP_400_BAD_REQUEST)
