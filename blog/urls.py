from django.conf.urls import url

from blog import views

urlpatterns = [
    url(r'^up_down/$', views.up_down),
    url(r'^comment/$', views.comment),

    url(r'^backend/add_article/$', views.add_article),

    url(r'(\w+)/(category|tag|archive)/(.+)/', views.home),  # 分类详情
    url(r'(\w+)/article/(\d+)/$', views.article_detail),  # 文章详情
    url(r'(\w+)', views.home),  # 个人主页
]