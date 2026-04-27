from rest_framework.response import Response

def success_response(data=None, message="Success", status=201):
    return Response({
        "success": True,
        "message": message,
        "data": data,
    }, status=status)


def error_response(errors='erorr', message="Error", status=400):
    return Response({
        "success": False,
        "message": message,
        "error": errors,
    }, status=status)

