from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Topic, Entry

class SearchTests(TestCase):
    """测试搜索功能"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        
        # 创建测试主题和内容
        self.topic1 = Topic.objects.create(text="Python Learning", owner=self.user)
        self.topic2 = Topic.objects.create(text="Django Web Development", owner=self.user)
        
        Entry.objects.create(topic=self.topic1, text="Introduction to Python basics.")
        Entry.objects.create(topic=self.topic2, text="Building a web app with Django.")

    def test_search_by_topic_title(self):
        """搜索主题标题"""
        response = self.client.get(reverse('learning_logs:topics'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Learning")
        self.assertNotContains(response, "Django Web Development")

    def test_search_by_entry_content(self):
        """搜索笔记内容"""
        response = self.client.get(reverse('learning_logs:topics'), {'q': 'web app'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Web Development")
        self.assertNotContains(response, "Python Learning")

    def test_search_no_results(self):
        """无匹配结果"""
        response = self.client.get(reverse('learning_logs:topics'), {'q': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results found for")
        self.assertNotContains(response, "Python Learning")
        self.assertNotContains(response, "Django Web Development")

    def test_empty_search(self):
        """空搜索返回所有主题"""
        response = self.client.get(reverse('learning_logs:topics'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Learning")
        self.assertContains(response, "Django Web Development")
