# learning_logs/views.py
from django.db.models.functions import Length
# learning_logs/views.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
# 导入所有模型和表单
from .models import Topic, Entry, EntryImage, EntryAttachment, EntryRevision, Like, Comment, Follow
from .forms import TopicForm, EntryForm, EntryImageForm, EntryAttachmentForm, CommentForm
# 导入图片压缩工具
from .utils import compress_image


def delete_file_if_exists(file_path):
    """删除文件（若存在），避免磁盘残留"""
    if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')

def search(request):
    """全局搜索 API - 返回 JSON 格式的搜索结果"""
    if not request.user.is_authenticated:
        return JsonResponse({'topics': [], 'entries': []})
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'topics': [], 'entries': []})
    
    # 搜索主题
    topics = Topic.objects.filter(
        owner=request.user,
        is_deleted=False,
        text__icontains=query
    )[:5]
    
    # 搜索笔记内容
    entries = Entry.objects.filter(
        topic__owner=request.user,
        is_deleted=False,
        text__icontains=query
    ).select_related('topic')[:10]
    
    results = {
        'topics': [{'id': t.id, 'text': t.text} for t in topics],
        'entries': [{
            'id': e.id,
            'topic_id': e.topic.id,
            'topic_text': e.topic.text,
            'text': e.text[:200]
        } for e in entries]
    }
    
    return JsonResponse(results)

@login_required
def topics(request):
    """显示所有的主题（带分页、搜索和多种排序）"""
    # 1. 获取搜索关键词、排序及时间过滤参数
    search_query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'date_desc')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if sort == 'date_asc':
        order_field = 'date_added'
    elif sort == 'date_desc':
        order_field = '-date_added'
    elif sort == 'name_asc':
        order_field = 'text'
    elif sort == 'name_desc':
        order_field = '-text'
    else:
        order_field = '-date_added'  # 默认最新优先
        sort = 'date_desc'

    topics = Topic.objects.filter(owner=request.user, is_deleted=False)
    
    if search_query:
        topics = topics.filter(
            Q(text__icontains=search_query) | Q(entry__text__icontains=search_query)
        ).distinct()
    
    if start_date:
        topics = topics.filter(date_added__date__gte=start_date)
    if end_date:
        topics = topics.filter(date_added__date__lte=end_date)
        
    topics = topics.order_by('-is_pinned', '-order', order_field)

    # 3. 初始化分页器：每页显示 5 个主题
    paginator = Paginator(topics, 5)

    # 4. 获取当前页码
    page_number = request.GET.get('page', 1)

    # 5. 获取当前页的主题列表
    page_obj = paginator.get_page(page_number)

    # 6. 把分页对象、搜索词和排序方式传给模板
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort': sort,
    }
    
    # 如果是 AJAX 请求，返回完整模板
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'learning_logs/topics.html', context)
    
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """显示单个主题的详细信息（笔记带分页 + 时间排序）"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    # 1.5 获取时间过滤参数
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # 2. 获取条目并应用过滤（排除已删除）
    base_entries = topic.entry_set.filter(is_deleted=False)
    
    if start_date:
        base_entries = base_entries.filter(date_added__date__gte=start_date)
    if end_date:
        base_entries = base_entries.filter(date_added__date__lte=end_date)

    if sort in ('date_asc', 'asc'):
        entries = base_entries.order_by('date_added')
    elif sort == 'len_asc':
        entries = base_entries.annotate(text_len=Length('text')).order_by('text_len')
    elif sort == 'len_desc':
        entries = base_entries.annotate(text_len=Length('text')).order_by('-text_len')
    else:
        entries = base_entries.order_by('-date_added')

    # 3. 初始化分页器
    paginator = Paginator(entries, 3)

    # 4. 获取当前页码
    page_number = request.GET.get('page', 1)

    # 5. 获取当前页的笔记列表
    page_obj = paginator.get_page(page_number)

    # 6. 把 topic、分页对象和参数传给模板
    context = {
        'topic': topic, 
        'page_obj': page_obj, 
        'sort': sort,
        'start_date': start_date,
        'end_date': end_date
    }
    
    # 如果是 AJAX 请求，只返回条目列表部分
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'learning_logs/topic.html', context)
    
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

# learning_logs/views.py
# 其他导入不变，只修改new_entry和edit_entry视图

# 修改：新增笔记+多文件上传（适配普通Form）
@login_required
def new_entry(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        # 处理笔记内容表单（ModelForm）
        entry_form = EntryForm(request.POST)
        # 多文件表单不用验证，直接取文件即可
        # image_form = EntryImageForm(request.POST, request.FILES)  # 注释掉
        # attachment_form = EntryAttachmentForm(request.POST, request.FILES)  # 注释掉

        if entry_form.is_valid():
            # 1. 先保存笔记
            new_entry = entry_form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()

            # 2. 处理多图片上传（直接从request.FILES取，不用表单验证）
            if 'image' in request.FILES:
                for image_file in request.FILES.getlist('image'):
                    entry_image = EntryImage(entry=new_entry, image=image_file)
                    entry_image.save()
                    # 自动压缩图片
                    image_abs_path = os.path.join(settings.MEDIA_ROOT, str(entry_image.image))
                    compress_image(image_abs_path)

            # 3. 处理多附件上传（直接从request.FILES取）
            if 'attachment' in request.FILES:
                for attach_file in request.FILES.getlist('attachment'):
                    EntryAttachment(entry=new_entry, attachment=attach_file).save()

            return redirect('learning_logs:topic', topic_id=topic_id)
    else:
        # GET请求：初始化空表单
        entry_form = EntryForm()
        image_form = EntryImageForm()  # 普通Form初始化
        attachment_form = EntryAttachmentForm()  # 普通Form初始化

    context = {
        'topic': topic,
        'entry_form': entry_form,
        'image_form': image_form,
        'attachment_form': attachment_form
    }
    return render(request, 'learning_logs/new_entry.html', context)

# 修改：编辑笔记+多文件管理（适配普通Form）
@login_required
def edit_entry(request, topic_id, entry_id):
    topic = get_object_or_404(Topic, id=topic_id)
    entry = get_object_or_404(Entry, id=entry_id)
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        # 处理笔记内容编辑
        old_text = entry.text  # 保存旧版本
        entry_form = EntryForm(request.POST, instance=entry)
        if entry_form.is_valid():
            new_entry = entry_form.save()
            
            # 保存历史版本（如果内容有变化）
            if old_text != new_entry.text:
                EntryRevision.objects.create(
                    entry=new_entry,
                    text=old_text,
                    created_by=request.user
                )

            # 1. 新增多图片（直接从request.FILES取）
            if 'image' in request.FILES:
                for image_file in request.FILES.getlist('image'):
                    entry_image = EntryImage(entry=entry, image=image_file)
                    entry_image.save()
                    compress_image(os.path.join(settings.MEDIA_ROOT, str(entry_image.image)))

            # 2. 新增多附件（直接从request.FILES取）
            if 'attachment' in request.FILES:
                for attach_file in request.FILES.getlist('attachment'):
                    EntryAttachment(entry=entry, attachment=attach_file).save()

            return redirect('learning_logs:topic', topic_id=topic_id)
    else:
        entry_form = EntryForm(instance=entry)
        image_form = EntryImageForm()  # 普通Form初始化
        attachment_form = EntryAttachmentForm()  # 普通Form初始化

    context = {
        'topic': topic,
        'entry': entry,
        'entry_form': entry_form,
        'image_form': image_form,
        'attachment_form': attachment_form,
        'entry_images': entry.images.all(),
        'entry_attachments': entry.attachments.all()
    }
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
def delete_entry_image(request, image_id):
    image = get_object_or_404(EntryImage, id=image_id)
    # 权限验证：只能删除自己的图片
    if image.entry.topic.owner != request.user:
        raise Http404
    # 删除服务器上的图片文件
    if image.image:
        delete_file_if_exists(os.path.join(settings.MEDIA_ROOT, str(image.image)))
    # 删除数据库记录
    image.delete()
    # 跳转回原笔记编辑页
    return redirect('learning_logs:edit_entry', topic_id=image.entry.topic.id, entry_id=image.entry.id)

# 新增：删除单个附件（单独写视图，处理文件删除）
@login_required
def delete_entry_attachment(request, attach_id):
    attachment = get_object_or_404(EntryAttachment, id=attach_id)
    # 权限验证：只能删除自己的附件
    if attachment.entry.topic.owner != request.user:
        raise Http404
    # 删除服务器上的附件文件
    if attachment.attachment:
        delete_file_if_exists(os.path.join(settings.MEDIA_ROOT, str(attachment.attachment)))
    # 删除数据库记录
    attachment.delete()
    # 跳转回原笔记编辑页
    return redirect('learning_logs:edit_entry', topic_id=attachment.entry.topic.id, entry_id=attachment.entry.id)

@login_required
def edit_topic(request, topic_id):
    """编辑已有主题"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = TopicForm(instance=topic)
    else:
        form = TopicForm(instance=topic, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topics')
    
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_topic.html', context)

@login_required
def delete_topic(request, topic_id):
    """软删除指定主题（移入回收站）"""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method == 'POST':
        from django.utils import timezone
        topic.is_deleted = True
        topic.deleted_at = timezone.now()
        topic.save()
        return redirect('learning_logs:topics')
    
    return redirect('learning_logs:topic', topic_id=topic_id)

@login_required
def delete_entry(request, topic_id, entry_id):
    """软删除指定笔记（移入回收站）"""
    topic = get_object_or_404(Topic, id=topic_id)
    entry = get_object_or_404(Entry, id=entry_id)
    if topic.owner != request.user or entry.topic != topic:
        raise Http404

    if request.method == 'POST':
        from django.utils import timezone
        entry.is_deleted = True
        entry.deleted_at = timezone.now()
        entry.save()
        return redirect('learning_logs:topic', topic_id=topic_id)
    
    return redirect('learning_logs:topic', topic_id=topic_id)

@login_required
def trash(request):
    """回收站页面"""
    deleted_topics = Topic.objects.filter(owner=request.user, is_deleted=True).order_by('-deleted_at')
    deleted_entries = Entry.objects.filter(topic__owner=request.user, is_deleted=True).select_related('topic').order_by('-deleted_at')
    
    context = {
        'deleted_topics': deleted_topics,
        'deleted_entries': deleted_entries,
    }
    return render(request, 'learning_logs/trash.html', context)

@login_required
def restore_topic(request, topic_id):
    """恢复已删除的主题"""
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=True)
    if topic.owner != request.user:
        raise Http404
    
    topic.is_deleted = False
    topic.deleted_at = None
    topic.save()
    return redirect('learning_logs:trash')

@login_required
def restore_entry(request, entry_id):
    """恢复已删除的笔记"""
    entry = get_object_or_404(Entry, id=entry_id, is_deleted=True)
    if entry.topic.owner != request.user:
        raise Http404
    
    entry.is_deleted = False
    entry.deleted_at = None
    entry.save()
    return redirect('learning_logs:trash')

@login_required
def permanent_delete_topic(request, topic_id):
    """永久删除主题"""
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=True)
    if topic.owner != request.user:
        raise Http404
    
    if request.method == 'POST':
        topic.delete()
    return redirect('learning_logs:trash')

@login_required
def permanent_delete_entry(request, entry_id):
    """永久删除笔记"""
    entry = get_object_or_404(Entry, id=entry_id, is_deleted=True)
    if entry.topic.owner != request.user:
        raise Http404
    
    if request.method == 'POST':
        entry.delete()
    return redirect('learning_logs:trash')

@login_required
def entry_revisions(request, topic_id, entry_id):
    """查看笔记修改历史"""
    topic = get_object_or_404(Topic, id=topic_id)
    entry = get_object_or_404(Entry, id=entry_id)
    if topic.owner != request.user or entry.topic != topic:
        raise Http404
    
    revisions = entry.revisions.all()
    
    context = {
        'topic': topic,
        'entry': entry,
        'revisions': revisions
    }
    return render(request, 'learning_logs/entry_revisions.html', context)

def share_topic(request, topic_id):
    """分享主题 - 公开访问"""
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)
    entries = topic.entry_set.filter(is_deleted=False).order_by('-date_added')
    
    context = {
        'topic': topic,
        'entries': entries,
        'is_shared': True
    }
    return render(request, 'learning_logs/shared_topic.html', context)

@login_required
def reorder_topics(request):
    """拖拽排序主题"""
    if request.method == 'POST':
        topic_ids = request.POST.getlist('topic_ids[]')
        for index, topic_id in enumerate(topic_ids):
            Topic.objects.filter(id=topic_id, owner=request.user).update(order=index)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_pin_topic(request, topic_id):
    """切换主题置顶状态"""
    if request.method == 'POST':
        topic = get_object_or_404(Topic, id=topic_id)
        if topic.owner != request.user:
            return JsonResponse({'status': 'error'}, status=403)
        topic.is_pinned = not topic.is_pinned
        topic.save()
        return JsonResponse({'status': 'success', 'is_pinned': topic.is_pinned})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_like(request, entry_id):
    """切换点赞状态"""
    if request.method == 'POST':
        entry = get_object_or_404(Entry, id=entry_id)
        # 检查权限：如果笔记是私人的，只有所有者可以点赞
        if entry.visibility == 'private' and entry.topic.owner != request.user:
            return JsonResponse({'status': 'error', 'message': '无权操作'}, status=403)
        # 检查是否已经点赞
        like, created = Like.objects.get_or_create(user=request.user, entry=entry)
        if not created:
            like.delete()
            return JsonResponse({'status': 'success', 'liked': False, 'like_count': entry.likes.count()})
        return JsonResponse({'status': 'success', 'liked': True, 'like_count': entry.likes.count()})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_comment(request, entry_id):
    """添加评论"""
    if request.method == 'POST':
        entry = get_object_or_404(Entry, id=entry_id)
        # 检查权限
        if entry.visibility == 'private' and entry.topic.owner != request.user:
            return JsonResponse({'status': 'error', 'message': '无权操作'}, status=403)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.entry = entry
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            comment.save()
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'id': comment.id,
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'replies': []
                }
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def follow_user(request, user_id):
    """关注用户"""
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, id=user_id)
        if user_to_follow == request.user:
            return JsonResponse({'status': 'error', 'message': '不能关注自己'}, status=400)
        follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
        if not created:
            follow.delete()
            return JsonResponse({'status': 'success', 'following': False, 'follower_count': user_to_follow.followers.count()})
        return JsonResponse({'status': 'success', 'following': True, 'follower_count': user_to_follow.followers.count()})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def user_profile(request, username):
    """用户个人资料页面"""
    user = get_object_or_404(User, username=username)
    topics = Topic.objects.filter(owner=user, is_deleted=False, visibility__in=['public', 'followers']).order_by('-date_added')
    # 检查是否是关注者
    is_following = False
    if request.user != user:
        is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
    # 只显示公开或对关注者可见的内容
    public_topics = topics.filter(visibility='public')
    if is_following:
        follower_topics = topics.filter(visibility='followers')
    else:
        follower_topics = []
    context = {
        'profile_user': user,
        'is_following': is_following,
        'public_topics': public_topics,
        'followers_count': user.followers.count(),
        'following_count': user.following.count(),
        'is_owner': request.user == user,
        'follower_topics': follower_topics,
    }
    return render(request, 'learning_logs/user_profile.html', context)

@login_required
def global_search(request):
    """全文搜索功能"""
    query = request.GET.get('q', '').strip()
    results = {
        'topics': [],
        'entries': [],
        'users': []
    }
    if query:
        # 搜索主题
        topics = Topic.objects.filter(
            Q(visibility='public') | Q(owner=request.user) | Q(visibility='followers', owner__in=request.user.following.values_list('followed_id', flat=True)),
            Q(text__icontains=query),
            is_deleted=False
        ).select_related('owner')[:10]
        results['topics'] = [{
            'id': t.id,
            'text': t.text,
            'owner': t.owner.username,
            'owner_id': t.owner.id
        } for t in topics]
        # 搜索笔记
        entries = Entry.objects.filter(
            Q(visibility='public') | Q(topic__owner=request.user) | Q(visibility='followers', topic__owner__in=request.user.following.values_list('followed_id', flat=True)),
            Q(text__icontains=query) | Q(topic__text__icontains=query),
            is_deleted=False
        ).select_related('topic', 'topic__owner')[:15]
        results['entries'] = [{
            'id': e.id,
            'text': e.text[:200],
            'topic_text': e.topic.text,
            'topic_id': e.topic.id,
            'owner': e.topic.owner.username,
            'owner_id': e.topic.owner.id
        } for e in entries]
        # 搜索用户
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id)[:5]
        results['users'] = [{
            'id': u.id,
            'username': u.username
        } for u in users]
    return JsonResponse(results)