

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .models import Todolist, User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
import csv
import io
import json
from datetime import datetime

# Create your views here.
@api_view(['POST'])
@permission_classes((AllowAny,))

def Signup(request):
        email  = request.data.get("email")
        password = request.data.get("password")
       
        name = request.data.get("name")
        if not name or not email or not password:
            return Response({'message':'All fields are required'})
        if User.objects.filter(email=email).exists():
            return  JsonResponse({'message':'Email already exist'})
        user = User.objects.create_user(email=email,password=password)
        user.name = name
        user.save()
        return JsonResponse({'message':'user created successsfully'} ,status = 200)

        

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])

def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key,'userid': user.id},status=HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addtask(request):
    if request.method == 'POST':
        user_id = request.user.id
        task = request.data.get('task')
        due_date = request.data.get('due_date')
    

        if not user_id or not task:
            return Response({'error': 'User ID and task are required'}, status=HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'error': 'User not found'}, status=HTTP_404_NOT_FOUND)

        new_task = Todolist(user=user, task=task, due_date=due_date)
        new_task.save()
        return Response({'message': 'Task added successfully'}, status=HTTP_200_OK)
    return Response({'error': 'Invalid request method'}, status=HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])


def gettasks(request):
    user_id = request.user.id
    now = datetime.now()

    # Filter upcoming tasks (due today or future), ordered by due_date
    tasks = Todolist.objects.filter(user_id=user_id, due_date__gte=now).order_by('due_date')

    if not tasks.exists():
        return Response({'message': 'No upcoming tasks found'}, status=HTTP_404_NOT_FOUND)

    task_list = [
        {
            'id': task.id,
            'task': task.task,
            'due_date': task.due_date,
            'status': task.status
        }
        for task in tasks
    ]

    return Response({'tasks': task_list}, status=HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_tasks(request):
    user_id = request.user.id
    query = request.GET.get('query', '')
    
    if not query:
        return Response({'error': 'Query parameter is required'}, status=HTTP_400_BAD_REQUEST)
    
    tasks = Todolist.objects.filter(user_id=user_id, task__icontains=query)
    task_list = [{'id': task.id, 'task': task.task, 'due_date': task.due_date} for task in tasks]
    
    return Response({'tasks': task_list}, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filter_tasks(request):
    user_id = request.user.id
    status = request.data.get('status', 'pending')  # ← use POST body

    if status not in ['pending', 'completed']:
        return Response({'error': 'Invalid status parameter'}, status=HTTP_400_BAD_REQUEST)

    tasks = Todolist.objects.filter(user_id=user_id, status=status)
    task_list = [{
        'id': task.id,
        'task': task.task,
        'due_date': task.due_date,
        'status': task.status   # ← include status in response!
    } for task in tasks]

    return Response({'tasks': task_list}, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])

def complete_task(request):
    task_id = request.data.get('task_id')
    
    if not task_id:
        return Response({'error': 'Task ID is required'}, status=HTTP_400_BAD_REQUEST)
    
    try:
        task = Todolist.objects.get(id=task_id, user=request.user)
        task.status = 'completed'
        task.save()
        return Response({'message': 'Task marked as completed'}, status=HTTP_200_OK)
    except Todolist.DoesNotExist:
        return Response({'error': 'Task not found'}, status=HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_task(request):
    task_id = request.data.get('task_id')
    new_task = request.data.get('updated_text')


    if not task_id or not new_task:
        return Response({'error': 'Task ID and new task are required'}, status=HTTP_400_BAD_REQUEST)

    try:
        task = Todolist.objects.get(id=task_id, user=request.user)
        task.task = new_task
       
        task.save()
        return Response({'message': 'Task updated successfully'}, status=HTTP_200_OK)
    except Todolist.DoesNotExist:
        return Response({'error': 'Task not found'}, status=HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_task(request):   
    task_id = request.data.get('task_id')
    
    if not task_id:
        return Response({'error': 'Task ID is required'}, status=HTTP_400_BAD_REQUEST)
    
    try:
        task = Todolist.objects.get(id=task_id, user=request.user)
        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=HTTP_200_OK)
    except Todolist.DoesNotExist:
        return Response({'error': 'Task not found'}, status=HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def import_tasks(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=HTTP_400_BAD_REQUEST)
    
    ext = file.name.split('.')[-1].lower()
    imported = 0

    try:
        if ext == 'json':
            data = json.load(file)
            for item in data:
                Todolist.objects.create(
                    user=request.user,
                    task=item.get('text', ''),
                    due_date=item.get('dueDate'),
                    status='completed' if item.get('completed') else 'pending'
                )
                imported += 1

        elif ext == 'csv':
            content = io.StringIO(file.read().decode('utf-8'))
            reader = csv.reader(content)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2:
                    Todolist.objects.create(
                        user=request.user,
                        task=row[0].strip(),
                        due_date=row[1].strip(),
                        status='completed' if len(row) > 2 and row[2].strip().lower().startswith('y') else 'pending'
                    )
                    imported += 1

        elif ext == 'txt':
            content = file.read().decode('utf-8')
            blocks = content.split('\n\n')
            for block in blocks:
                lines = block.strip().split('\n')
                task, due, completed = '', '', False
                for line in lines:
                    if line.startswith('Task:'): task = line[5:].strip()
                    elif line.startswith('Due:'): due = line[4:].strip()
                    elif line.startswith('Completed:'): completed = 'yes' in line.lower()
                if task and due:
                    Todolist.objects.create(user=request.user, task=task, due_date=due, status='completed' if completed else 'pending')
                    imported += 1

        elif ext == 'sql':
            content = file.read().decode('utf-8')
            import re
            pattern = r"INSERT INTO tasks.*?VALUES\s*\('(.+?)',\s*'(.+?)',\s*(\d)\);"
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                Todolist.objects.create(
                    user=request.user,
                    task=match[0],
                    due_date=match[1],
                    status='completed' if match[2] == '1' else 'pending'
                )
                imported += 1

        else:
            return Response({'error': 'Unsupported file type'}, status=HTTP_400_BAD_REQUEST)

        return Response({'message': f'{imported} tasks imported successfully'}, status=HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Import failed: {str(e)}'}, status=HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])  

def export_tasks(request, file_format):
    print(file_format)
    user = request.user  # assuming the user is authenticated
    tasks = Todolist.objects.filter(user=user).values('task', 'due_date', 'status')

    if file_format == 'json':
        response = HttpResponse(json.dumps(list(tasks), default=str), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=tasks.json'
        return response

    elif file_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=tasks.csv'
        writer = csv.writer(response)
        writer.writerow(['Task', 'Due Date', 'Status'])
        for task in tasks:
            due_date = task['due_date']
            due_str = due_date.strftime('%d-%m-%Y') if due_date else ''
            writer.writerow([task['task'], due_str, task['status']])
        return response  # ← Move return outside the loop

    elif file_format == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=tasks.txt'
        for task in tasks:
            due_date = task['due_date']
            due_str = due_date.strftime('%d-%m-%Y') if due_date else 'No Due Date'
            response.write(f"{task['task']} | {due_str} | {task['status']}\n")
        return response

    elif file_format == 'sql':
        response = HttpResponse(content_type='text/sql')
        response['Content-Disposition'] = 'attachment; filename=tasks.sql'
        for task in tasks:
            due_date = task['due_date']
            due_str = f"'{due_date.strftime('%Y-%m-%d')}'" if due_date else 'NULL'
            sql = f"INSERT INTO todolist (task, due_date, status) VALUES ('{task['task']}', {due_str}, '{task['status']}');\n"
            response.write(sql)
        return response

    else:
        return HttpResponse("Unsupported file_format", status=400)