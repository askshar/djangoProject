from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.


def register_view(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            auth.login(request, user)
            messages.success(request, "Logged In successfully.")
            return redirect('home')


    return render(request, 'base/login_register.html', {'page': page, 'form': form})



def login_view(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST['username'].lower()
            password = request.POST['password']

            try:
                user = User.objects.get(username=username)
            except:
                messages.error(request, 'User does not exist.')

            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                messages.success(request, 'Logged In successfully.')
                return redirect('home')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_view(request):
    auth.logout(request)
    return redirect('login')


def home(request):
    q = request.GET.get('q')
    if q:
        rooms = Room.objects.filter(Q(topic__topic__icontains=q) |
                                    Q(name__icontains=q) |
                                    Q(description__icontains=q)).order_by('-created')
        room_count = rooms.count()
        room_messages = Message.objects.filter(room__topic__topic__icontains=q).order_by('-created')
    else:
        rooms = Room.objects.all().order_by('-created')
        room_count = rooms.count()
        room_messages = Message.objects.all().order_by('-created')
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    participants_count = participants.count()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST['body']
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
        'participants_count': participants_count
    }
    return render(request, 'base/room.html', context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user == room.host:
        if request.method == 'POST':
            form = RoomForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                return redirect('home')
    else:
        return HttpResponse("Unauthorized request!")

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user == room.host:
        if request.method == 'POST':
            room.delete()
            return redirect('home')
    else:
        return HttpResponse("Unauthorized request!")
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user == message.user:
        if request.method == 'POST':
            message.delete()
            return redirect('home')
    else:
        return HttpResponse("Unauthorized request!")
    return render(request, 'base/delete.html', {'obj': message})

