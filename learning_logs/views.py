# learning_logs/views.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
import os
from django.conf import settings

def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """显示所有的主题（带分页和搜索）"""
    # 1. 获取搜索关键词
    search_query = request.GET.get('q', '')

    # 2. 先取所有数据，如果搜索词存在则过滤
    if search_query:
        # 同时搜索主题名称和笔记内容，使用 distinct() 避免重复
        topics = Topic.objects.filter(
            Q(owner=request.user) & 
            (Q(text__icontains=search_query) | Q(entry__text__icontains=search_query))
        ).distinct().order_by('date_added')
    else:
        topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    
    # 3. 初始化分页器：每页显示 5 个主题
    paginator = Paginator(topics, 5)
    
    # 4. 获取当前页码
    page_number = request.GET.get('page', 1)
    
    # 5. 获取当前页的主题列表
    page_obj = paginator.get_page(page_number)
    
    # 6. 把分页对象和搜索词传给模板
    context = {'page_obj': page_obj, 'search_query': search_query}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """显示单个主题的详细信息（笔记带分页）"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404
    
    # 1. 先取该主题下的所有笔记
    entries = topic.entry_set.order_by('-date_added')
    
    # 2. 初始化分页器：每页显示 3 条笔记（你可以改成10、15）
    paginator = Paginator(entries, 3)
    
    # 3. 获取当前页码
    page_number = request.GET.get('page', 1)
    
    # 4. 获取当前页的笔记列表
    page_obj = paginator.get_page(page_number)
    
    # 5. 把 topic 和分页对象传给模板
    context = {'topic': topic, 'page_obj': page_obj}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """添加新主题"""
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """在特定主题下添加新条目"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        # 关键：上传文件需要用 request.FILES
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    else:
        form = EntryForm()

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, topic_id, entry_id):
    """编辑既有条目"""
    topic = get_object_or_404(Topic, id=topic_id)
    entry = get_object_or_404(Entry, id=entry_id)
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        # 关键：上传文件需要用 request.FILES，且传入instance
        form = EntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            # 如果用户清空了图片/附件，删除旧文件
            if 'image-clear' in request.POST and entry.image:
                delete_file_if_exists(os.path.join(settings.MEDIA_ROOT, str(entry.image)))
            if 'attachment-clear' in request.POST and entry.attachment:
                delete_file_if_exists(os.path.join(settings.MEDIA_ROOT, str(entry.attachment)))
            
            form.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    else:
        form = EntryForm(instance=entry)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
def edit_topic(request, topic_id):
    """编辑已有主题"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = TopicForm(instance=topic)
    else:
        form = TopicForm(instance=topic, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topics')
    
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_topic.html', context)

@login_required
def delete_topic(request, topic_id):
    """删除指定主题"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        topic.delete()
        return redirect('learning_logs:topics')
    
    return redirect('learning_logs:topic', topic_id=topic_id)

@login_required
def delete_entry(request, topic_id, entry_id):
    """删除指定笔记"""
    topic = get_object_or_404(Topic, id=topic_id)
    entry = get_object_or_404(Entry, id=entry_id)
    if topic.owner != request.user or entry.topic != topic:
        raise Http404

    if request.method == 'POST':
        entry.delete()
        return redirect('learning_logs:topic', topic_id=topic_id)
    
    return redirect('learning_logs:topic', topic_id=topic_id)

    # 新增：删除文件的辅助函数（避免文件残留）
def delete_file_if_exists(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)