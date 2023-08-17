import json

class Response():
    def __init__(self, status=0, success=False, message=None, code=500, data=None):
        self.status = status
        self.success=success
        self.message=message
        self.code=code
        self.data=data

    def values(self):
        return {
            "status": self.status,
            "success": self.success,
            "message": self.message,
            "code": self.code,
            "data": self.data
        }
    

res = Response(code=201).values()
print(json.dumps(res))