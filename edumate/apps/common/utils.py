import secrets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler


class ResponseMessage:
    
    @staticmethod
    def success(message: str, data: dict = None, status: int = status.HTTP_200_OK) -> Response:
        return Response({
            "status": True,
            "message": message,
            "data": data,
        }, status=status)
        
    @staticmethod
    def error(message: str, data: dict = None, status: int = status.HTTP_400_BAD_REQUEST) -> Response:
        return Response({
            "status": False,
            "message": message,
            "data": data,
        }, status=status)
        
        
def custom_exceptions_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "status": False,
            "message": "Request failed!",
            "data": response.data,
        }
    return response



def create_code(code:int=6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(code))



