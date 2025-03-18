# Create your views here.
import datetime

from rest_framework.decorators import api_view, authentication_classes, throttle_classes

from myapp import utils
from myapp.auth.authentication import TokenAuthtication
from myapp.auth.throttling import MyRateThrottle
from myapp.handler import APIResponse
from myapp.models import User
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
def login(request):
    username = request.data['username']
    password = utils.md5value(request.data['password'])

    users = User.objects.filter(username=username, password=password)
    if len(users) > 0:
        user = users[0]

        if user.role in ['1', '3']:
            return APIResponse(code=1, msg='This account is an admin account')

        data = {
            'username': username,
            'password': password,
            'token': md5value(username)  # Generate token
        }
        serializer = UserSerializer(user, data=data)
        if serializer.is_valid():
            serializer.save()
            make_login_log(request)
            return APIResponse(code=0, msg='Login successful', data=serializer.data)
        else:
            print(serializer.errors)

    return APIResponse(code=1, msg='Incorrect username or password')


@api_view(['POST'])
@throttle_classes([MyRateThrottle])
def register(request):
    print(request.data)
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    repassword = request.data.get('repassword', None)
    if not username or not password or not repassword:
        return APIResponse(code=1, msg='Username or password cannot be empty')
    if password != repassword:
        return APIResponse(code=1, msg='Passwords do not match')
    users = User.objects.filter(username=username)
    if len(users) > 0:
        return APIResponse(code=1, msg='Username already exists')

    data = {
        'username': username,
        'password': password,
        'role': 2,  # Role 2
        'status': 0,
    }
    data.update({'password': utils.md5value(request.data['password'])})
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='Registration successful', data=serializer.data)
    else:
        print(serializer.errors)

    return APIResponse(code=1, msg='Registration failed')


@api_view(['GET'])
def info(request):
    if request.method == 'GET':
        pk = request.GET.get('id', -1)
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user)
        return APIResponse(code=0, msg='Query successful', data=serializer.data)


@api_view(['POST'])
@authentication_classes([TokenAuthtication])
def update(request):
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
    if 'role' in data.keys():
        del data['role']
    serializer = UserSerializer(user, data=data)
    print(serializer.is_valid())
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='Update successful', data=serializer.data)
    else:
        print(serializer.errors)

    return APIResponse(code=1, msg='Update failed')


@api_view(['POST'])
@authentication_classes([TokenAuthtication])
def updatePwd(request):

    try:
        pk = request.GET.get('id', -1)
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return APIResponse(code=1, msg='Object does not exist')

    print(user.role)
    if user.role != '2':
        return APIResponse(code=1, msg='Invalid parameter')

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