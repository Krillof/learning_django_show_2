from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Directory, AllowedToDirectory, Picture
from .forms import UploadFileForm

# It's not a view!!!!!
def make_context_for_index(request, error_message):
    context = {'is_auth': request.user.is_authenticated}

    if request.user.is_authenticated:
        context['username'] = request.user.username
        context['dirs'] = [d.name for d in Directory.objects.filter(creator=request.user)]
        context['frienddirs'] = [{'dirname':d.directory.name, 'username':d.directory.creator.username} for d in AllowedToDirectory.objects.filter(user=request.user)]
    else:
        context['username'] = ''

    context['error_message'] = error_message
    return context
# It's not a view!!!!!








def index(request):
    return render(request, 'mainapp/index.html', make_context_for_index(request, ''))

def register(request):
    username = request.POST['username']
    password = request.POST['password']

    if username == '' or password == '':
        return render(request, 'mainapp/index.html', make_context_for_index(request, 'password or username is empty'))
    else:
        if User.objects.filter(username=username).count() > 0:
            return render(request, 'mainapp/index.html', make_context_for_index(request, 'Пользователь с таким именем уже есть'))
        else:
            user = User.objects.create(username=username)
            user.set_password(password) # Так правильнее! Почему-то здесь работает только там, а в прошлом проекте можно было и не так.
            user.save()

            login(request, user)

    return redirect('/')

def enter(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if not (user is None):
        login(request, user)
    else:
        if User.objects.filter(username=username).count() > 0:
            return render(request, 'mainapp/index.html', make_context_for_index(request, 'Неверный пароль'))
        else:
            return render(request, 'mainapp/index.html', make_context_for_index(request, 'Пользователя с таким логином не существует'))

    return redirect('/')

@login_required(redirect_field_name='/')
def exit(request):
    logout(request)
    return redirect('/')

@login_required(redirect_field_name='/')
def dirs(request, username, dir):
    is_guest = request.user.username != username
    if is_guest:
        u = get_object_or_404(User, username=username)
        d = get_object_or_404(Directory, name=dir, creator=u)
        allow_query = AllowedToDirectory.objects.filter(directory=d, user=request.user)
        is_allowed = allow_query.count() > 0
        if is_allowed:
            pictures =  [p.picture for p in Picture.objects.filter(directory=d)]
            context = {'dirname':dir, 'pictures':pictures, 'is_guest':is_guest, 'creator':username, 'can_add':allow_query[0].can_add}
            return render(request, 'mainapp/dir.html', context)
        else:
            return redirect('/')
    else:
        d = get_object_or_404(Directory, name=dir, creator=request.user)
        pictures = [p.picture for p in Picture.objects.filter(directory=d)]
        context = {'dirname':dir, 'pictures':pictures, 'is_guest':is_guest, 'creator':username, 'can_add': True}
        return render(request, 'mainapp/dir.html', context)

@login_required(redirect_field_name='/')
def createdir(request):
    name = request.POST['directory_name']
    
    if Directory.objects.filter(name=name, creator=request.user).count() == 0:
        d = Directory.objects.create(name=name, creator=request.user)
        d.save()

        # Нужно поставить запрет на некоторые символы - не все символы могут быть в адресной строке
        # ... или Django с этим справляется? ...
        return redirect('/dirs/'+request.user.username+'/'+name+'/')
    else:
        return render(request, 'mainapp/index.html', make_context_for_index('Папка с таким именем у вас уже есть'))

@login_required(redirect_field_name='/')
def addallowtouser(request, dir):

    username = request.POST['username']
    can_add = (request.POST['can_add'] == 'checked')

    u = get_object_or_404(User, username=username)
    d = get_object_or_404(Directory, name=dir, creator=request.user)
    a = AllowedToDirectory.objects.create(directory=d, user=u, can_add=can_add)
    a.save()

    # Занимательно, но если в начале в redirect в первом аргументе есть
    # символ /, то текущий путь заменяется
    # а если нет - дописывается
    # Например, вы заходите на /t/ и вас redirect на /b/
    # то будет /t/b/
    # А если redirect на b/, то будет /b/

    return redirect('/dirs/'+request.user.username+'/'+dir+'/')

@login_required(redirect_field_name='/')
def addpicturetodir(request, dir):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            d = get_object_or_404(Directory, name=dir, creator=request.user)
            try:
                pic = request.FILES['file']
                instance = Picture.objects.create(directory=d, name=pic.name, picture=pic)
                instance.save()
            except:
                print('error')
        else:
            print(form.errors)
    else:
        form = UploadFileForm()
    return redirect('/dirs/'+request.user.username+'/'+dir+'/')