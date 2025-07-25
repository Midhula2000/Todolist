
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
from todo.models import  User,Todolist, UserActivity
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.db.models import F, Sum

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





@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])

def user_report(request):
    date_param = request.GET.get('date')  # Check for date filter
    if date_param:
        date_obj = parse_date(date_param)
        users = User.objects.filter(date_joined__date=date_obj)
    else:
        users = User.objects.order_by('-date_joined')[:6]  # Recent 6 users

    data = [
        {
            'name': user.name,
            'email': user.email,
            'joined': user.date_joined.strftime('%Y-%m-%d')
        }
        for user in users
    ]
    return Response(data, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_usage_report(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 6))

    report = []

    for user in User.objects.all():
        total_tasks = Todolist.objects.filter(user=user).count()
        completed_tasks = Todolist.objects.filter(user=user, status='completed').count()
        edited_tasks = Todolist.objects.filter(user=user).exclude(created_at=F('updated_at')).count()

        # Aggregate import/export task counts
        exported = UserActivity.objects.filter(user=user, action_type='export').aggregate(total=Sum('task_count'))['total'] or 0
        imported = UserActivity.objects.filter(user=user, action_type='import').aggregate(total=Sum('task_count'))['total'] or 0

        report.append({
            'name': user.name,
            'email': user.email,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'edited_tasks': edited_tasks,
            'deleted_tasks': 0,        # Still a placeholder
            'exported_count': exported,
            'imported_count': imported,
        })

    # Sort by total tasks (descending)
    report.sort(key=lambda x: x['total_tasks'], reverse=True)

    # Paginate
    paginator = Paginator(report, page_size)
    page_obj = paginator.get_page(page)

    return Response({
        'results': list(page_obj),
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }, status=HTTP_200_OK)