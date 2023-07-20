from django.shortcuts import render, redirect
from board.models import Board, Comment, Book
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
import os, math
from urllib.parse import quote
from django.http.response import HttpResponse
from django.http import response
import chunk
from django.db.models import Q
from pip._internal import req
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from board import bigdataPro


# Create your views here.
UPLOAD_DIR='c:/ksj/upload/'

#홈화면 가는것
def home(request):
    return render(request, 'main.html') 


# 리스트 출력하는법(1)
# def list(request):
#     boardCount=Board.objects.all().count()
#     boardList=Board.objects.all().order_by("-bno") #bno내림차순 정렬
#     return render(request, 'board/list.html', {"boardList":boardList, "boardCount":boardCount})

@csrf_exempt
def list(request):
    try:
        search_option=request.POST['search_option']
        print(search_option)
    except:
        search_option=''
        
    try: 
        search=request.POST['search']
    except:
        search=''
        
    if search_option=='all':
        boardCount=Board.objects.filter(Q(writer__contains=search)
                                        | Q(title__cotains=search)
                                        | Q(content__contains = search)).count()
                                        
        # boardList=Board.objects.filter(Q(writer__contains=search)
        #                                 | Q(title__cotains=search)
        #                                 | Q(content__contains = search))._order_by('-bno')
    elif search_option=="w":
        boardCount=Board.objects.filter(Q(writer__contains=search)).count()
    elif search_option=="t":
        boardCount=Board.objects.filter(Q(title__contains=search)).count()
    elif search_option=="c":
        boardCount=Board.objects.filter(Q(content__contains=search)).count()
    else:
        boardCount=Board.objects.all().count()
        
    try:
        start=int(request.GET['start']) #start=페이지의 첫번째 데이터
    except:
        start=0
        
        
    page_size=5
    block_size=5    
    end=start+page_size #1page:start=0 / end=5 [start:end]
    
    total_page=math.ceil(boardCount/page_size)
    current_page=math.ceil((start+1)/page_size)
    start_page=math.floor((current_page-1)/block_size)*block_size+1
    end_page = start_page + block_size -1
    
    if end_page > total_page:
        end_page=total_page
        
    if start_page >= block_size:
        prev_list = (start_page-2)*page_size
    else:
        prev_list = 0
        
    if total_page > end_page:
        next_list = end_page * page_size
    else:
        next_list = 0
    
    
    if search_option =='all':
        boardList = Board.objects.filter(Q(writer__contains=search)|
                                         Q(title__contains=search)|
                                         Q(content__contains=search)).order_by('-bno')[start:end]    
    elif search_option =='w':
        boardList = Board.objects.filter(Q(writer__contains=search)).order_by('-bno')[start:end]
    elif search_option =='t':
        boardList = Board.objects.filter(Q(title__contains=search)).order_by('-bno')[start:end]
    elif search_option =='c':
        boardList = Board.objects.filter(Q(content__contains=search)).order_by('-bno')[start:end]
    else:
        boardList = Board.objects.all().order_by('-bno')[start:end]
        
    
    links=[]
    
    for i in range(start_page, end_page+1):
        page_start = (i-1)*page_size
        link = "<a href='/list?start="+str(page_start)+"'>"+str(i)+"</a>"
        links.append(link)
    
    return render(request, 'board/list.html',
                  {
                      'boardList':boardList,
                      'boardCount':boardCount,
                      'search':search,
                      'search_option':search_option,
                      'start_page':start_page,
                      'end_page':end_page,
                      'total_page':total_page,
                      'block_size':block_size,
                      'prev_list':prev_list,
                      'next_list':next_list,
                      'links':links,
                      })
    
    

@login_required #<-로그인한 사용자만 글쓰게 하려고 하는경우
def register(request):
    return render(request, 'board/register.html')

@csrf_exempt
def insert(request):
    fname=''
    fsize=0
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        
        fp=open("%s%s"%(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        
    t = request.POST['title']
    w = request.POST['writer']
    c = request.POST['content']
    dto = Board(title=t, writer=w, content=c, filename=fname, filesize=fsize)
    dto.save()
    return redirect('/list/')
        
def download(request):
    no=request.GET['bno']
    dto=Board.objects.get(bno=no)
    path=UPLOAD_DIR+dto.filename
    filename=os.path.basename(path)
    filename=quote(filename)
    with open(path, 'rb') as file:
        response=HttpResponse(file.read(), content_type='application/actet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8''{0}".format(filename)
        
    dto.down_up()
    dto.save()
    return response

def detail(request):
    no=request.GET['bno']
    dto=Board.objects.get(bno=no)
    dto.hit_up()
    dto.save()
    
    #댓글 커맨트 가져와야함 /여러개 가져올때는 filter를 사용
    commentList = Comment.objects.filter(bno=no).order_by("-cno") #-는 ㄴㅐ림차순
    
    
    filesize="%.2f"%(dto.filesize/1024)
    return render(request, 'board/detail.html', 
                  {'dto':dto, 'filesize':filesize, 'commentList':commentList})

@csrf_exempt
def update(request):
    no=request.POST['bno']
    dto_src=Board.objects.get(bno=no)
    fname=dto_src.filename
    fsize=dto_src.filesize
    
    if 'file' in request.FILES:
        file=request.FILES['file']
        fname=file.name
        fsize=file.size
        fp=open('%s%s'%(UPLOAD_DIR, fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        
    dto_new=Board(bno=no,
                  writer=request.POST['writer'], 
                  title=request.POST['title'], 
                  content=request.POST['content'], 
                  hit=dto_src.hit,
                  down=dto_src.down,
                  filename=fname, 
                  filesize=fsize)
    dto_new.save()
    return redirect("/list/")

@csrf_exempt
def delete(request):
    no=request.POST['bno']
    Board.objects.get(bno=no).delete()
    return redirect("/list/")

#댓글관련 함수들

@csrf_exempt
def reply_insert(request):
    no=request.POST['bno']
    dto=Comment(bno=no,
                writer=request.POST['writer'],
                content=request.POST['content'])
    dto.save()
    return redirect("/detail?bno="+no)
    

#회원가입

def signup_form(request):
    return render(request, 'user/signup.html')

@csrf_exempt
def signup(request):
    if request.method=='POST':
        if request.POST['password']==request.POST['password2']:
            username=request.POST['username']
            password=request.POST['password']
            email=request.POST['email']
            user=User.objects.create_user(username, email, password)
        return redirect('/login_form')
    return render(request, 'user/signup.html')



def login_form(request):
    return render(request, 'user/login.html')

@csrf_exempt
def login(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user=auth.authenticate(request, username=username, password=password)
        
        if user is not None :
            auth.login(request, user)    
            return redirect("/") #<-첫번째 홈페이지로 로그인되서 돌아가게 함
        else:
            return render(request, 'user/login.html', {'error':'username/password is incorrect'})
        
    else:
        return render(request, 'user/login.html')

def logout(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, 'user/login.html')

# CCTV가져오기

def cctv_map(request):
    bigdataPro.cctv_map()
    return render(request, 'map/map01.html')


#웹 그롤링
def webcraw(request):
    data = []
    bigdataPro.web_craw(data)
    
    for book in data:
        dto = Book(title = book[0], author = book[1], price = book[2], point = book[3])
        dto.save()
        
    return redirect("/")

#그래프 그리기ㅇ
def chart(request):
    data=Book.objects.all().values_list('title','point')
    print(data)
    bigdataPro.makeChart(data)
    return render(request, 'bigdata/chart.html', {'data':data})


    
    