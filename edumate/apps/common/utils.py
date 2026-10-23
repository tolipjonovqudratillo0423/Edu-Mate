from rest_framework.response import Response
from rest_framework import status

class ResponseMessage:
    
    @staticmethod
    def success(message: str, data: dict = None) -> Response:
        return Response({
            "status": True,
            "message": message,
            "data": data,
        }, status=status.HTTP_200_OK)
        
    @staticmethod
    def error(message: str, data: dict = None) -> Response:
        return Response({
            "status": False,
            "message": message,
            "data": data,
        }, status=status.HTTP_400_BAD_REQUEST)