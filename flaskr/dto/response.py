import json

class Response():
    def __init__(self, status=1, success=False, message=None, code=500, result=None):
        self.status = status
        self.success=success
        self.message=message
        self.code=code
        self.result=result

    def values(self):
        return {
            "status": 1,
            "success": self.success,
            "message": self.message,
            "code": 200 if self.success else self.code,
            "result": self.result
        }