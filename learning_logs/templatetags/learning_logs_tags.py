import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(text):
    """
    将 Markdown 文本转换为 HTML
    支持代码高亮、表格、自动链接等扩展
    """
    md = markdown.Markdown(
        extensions=[
            'fenced_code',      # 代码块
            'codehilite',       # 代码高亮
            'tables',           # 表格
            'toc',              # 目录
            'nl2br',            # 换行转 <br>
            'sane_lists',       # 智能列表
        ]
    )
    html = md.convert(text)
    return mark_safe(html)

@register.filter(name='highlight')
def highlight_filter(text, query):
    """
    高亮搜索关键词
    """
    if not query:
        return text
    
    from django.utils.html import escape
    import re
    
    escaped_text = escape(text)
    escaped_query = escape(query)
    
    pattern = re.compile(f'({re.escape(escaped_query)})', re.IGNORECASE)
    highlighted = pattern.sub(
        r'<mark style="background: rgba(99, 102, 241, 0.3); color: var(--primary); padding: 0.1rem 0.2rem; border-radius: 3px;">\1</mark>',
        escaped_text
    )
    return mark_safe(highlighted)

@register.filter(name='video_embed')
def video_embed(url):
    """
    将普通视频链接转换为嵌入链接(针对Bilibili/Youtube)
    """
    if not url:
        return ""
    
    # Bilibili
    if 'bilibili.com' in url:
        import re
        bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
        if bv_match:
            bv = bv_match.group()
            return f"https://player.bilibili.com/player.html?bvid={bv}&page=1&high_quality=1&danmaku=0"
    
    # Youtube
    if 'youtube.com' in url or 'youtu.be' in url:
        import re
        yt_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
        if yt_match:
            v_id = yt_match.group(1)
            return f"https://www.youtube.com/embed/{v_id}"
            
    return url

@register.filter(name='has_liked')
def has_liked(entry, user):
    """
    判断用户是否已经点赞了该笔记
    """
    if user.is_anonymous:
        return False
    return entry.likes.filter(user=user).exists()
