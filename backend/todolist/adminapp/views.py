
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from todo.models import  User


@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))

def admin_login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    if not user.is_admin:
        return Response({'error': 'You do not have admin privileges'},
                        status=HTTP_403_FORBIDDEN)
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({'token': token.key, 'message': 'Login successful'},
                    status=HTTP_200_OK)


