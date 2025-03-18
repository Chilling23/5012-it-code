# Create your views here.
import datetime

from rest_framework.decorators import api_view, authentication_classes

from myapp import utils
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import User
from myapp.permission.permission import isDemoAdminUser
from myapp.serializers import UserSerializer, LoginLogSerializer
from myapp.utils import md5value


def make_login_log(request):
    try:
        username = request.data['username']
        data = {
            "username": username,
            "ip": utils.get_ip(request),
            "ua": utils.get_ua(request)
        }
        serializer = LoginLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
    except Exception as e:
        print(e)


@api_view(['POST'])
def admin_login(request):
    username = request.data['username']
    password = utils.md5value(request.data['password'])

    users = User.objects.filter(username=username, password=password, role__in=['1', '3'])
    if len(users) > 0:
        user = users[0]
        data = {
            'username': username,
            'password': password,
            'admin_token': md5value(username)  # Generate token
        }
        serializer = UserSerializer(user, data=data)
        if serializer.is_valid():
            serializer.save()
            make_login_log(request)
            return APIResponse(code=0, msg='Login successful', data=serializer.data)
        else:
            print(serializer.errors)

    return APIResponse(code=1, msg='Incorrect username or password')


@api_view(['GET'])
def info(request):
    if request.method == 'GET':
        pk = request.GET.get('id', -1)
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user)
        return APIResponse(code=0, msg='Query successful', data=serializer.data)


@api_view(['GET'])
def list_api(request):
    if request.method == 'GET':
        keyword = request.GET.get("keyword", '')
        users = User.objects.filter(username__contains=keyword).order_by('-create_time')
        serializer = UserSerializer(users, many=True)
        return APIResponse(code=0, msg='Query successful', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def create(request):
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='Demo account cannot perform this action')

    print(request.data)
    if not request.data.get('username', None) or not request.data.get('password', None):
        return APIResponse(code=1, msg='Username or password cannot be empty')
    users = User.objects.filter(username=request.data['username'])
    if len(users) > 0:
        return APIResponse(code=1, msg='Username already exists')

    data = request.data.copy()
    data.update({'password': utils.md5value(request.data['password'])})
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='Creation successful', data=serializer.data)
    else:
        print(serializer.errors)

    return APIResponse(code=1, msg='Creation failed')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def update(request):
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='Demo account cannot perform this action')

    try:
        pk = request.GET.get('id', -1)
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return APIResponse(code=1, msg='Object does not exist')

    data = request.data.copy()
    if 'username' in data.keys():
        del data['username']
    if 'password' in data.keys():
        del data['password']
    serializer = UserSerializer(user, data=data)
    print(serializer.is_valid())
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='Update successful', data=serializer.data)
    else:
        print(serializer.errors)
    return APIResponse(code=1, msg='Update failed')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def updatePwd(request):
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='Demo account cannot perform this action')

    try:
        pk = request.GET.get('id', -1)
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return APIResponse(code=1, msg='Object does not exist')

    password = request.data.get('password', None)
    newPassword1 = request.data.get('newPassword1', None)
    newPassword2 = request.data.get('newPassword2', None)

    if not password or not newPassword1 or not newPassword2:
        return APIResponse(code=1, msg='Cannot be empty')

    if user.password != utils.md5value(password):
        return APIResponse(code=1, msg='Incorrect original password')

    if newPassword1 != newPassword2:
        return APIResponse(code=1, msg='Passwords do not match')

    data = request.data.copy()
    data.update({'password': utils.md5value(newPassword1)})
    serializer = UserSerializer(user, data=data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='Update successful', data=serializer.data)
    else:
        print(serializer.errors)

    return APIResponse(code=1, msg='Update failed')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def delete(request):
    if isDemoAdminUser(request):
        return APIResponse(code=1, msg='Demo account cannot perform this action')

    try:
        ids = request.GET.get('ids')
        ids_arr = ids.split(',')
        User.objects.filter(id__in=ids_arr).delete()
    except User.DoesNotExist:
        return APIResponse(code=1, msg='Object does not exist')

    return APIResponse(code=0, msg='Deletion successful')