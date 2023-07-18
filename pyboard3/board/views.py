from django.shortcuts import render, redirect
from board.models import Board
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
UPLOAD_DIR='c:/ksj/upload/'


def list(request):
    boardCount=Board.objects.all().count()
    boardList=Board.objects.all().order_by("-bno") #bno내림차순 정렬
    return render(request, 'board/list.html', {"boardList":boardList, "boardCount":boardCount})

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
        
        fp=open("%s%s" %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        
        t = request.POST['title']
        w = request.POST['writer']
        c = request.POST['content']
        dto = Board(title=t, writer=w, content=c, filename=fname, filesize=fsize)
        dto.save()
        return redirect('/list/')
        
