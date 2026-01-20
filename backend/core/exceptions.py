from django.http import JsonResponse
from rest_framework import status

def handler404(request, exception=None):
    """
    Custom 404 error handler that returns a JSON response.
    """
    response = JsonResponse(
        {"error": "Not Found", "message": "The requested resource was not found."},
        status=status.HTTP_404_NOT_FOUND,
    )
    return response

def handler500(request):
    """
    Custom 500 error handler that returns a JSON response.
    """
    response = JsonResponse(
        {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return response
