import json
from bbs import settings
import os
from django.contrib import auth
from django.db.models import Count, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from geetest import GeetestLib
from bs4 import BeautifulSoup
from blog import forms, models
import logging

# 生成logger实例来记录日志
logger = logging.getLogger(__name__)


def home(request, username, *args):
    """个人博客主页"""
    logger.debug("home视图获取的用户名:{}".format(username))

    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        logger.warning("页面不存在")
        return HttpResponse("404")
    blog = user.blog
    if not args:
        logger.debug("args没有接收到参数,默认走用户的个人博客页面")
        # 用户所有文章的信息
        article_list = models.Article.objects.filter(user=user)
    else:
        logger.debug(args)
        # 按照文章的分类或标签或日期归档来查询
        if args[0] == "category":
            article_list = models.Article.objects.filter(user=user).filter(category__title=args[1])
        elif args[0] == "tag":
            article_list = models.Article.objects.filter(user=user).filter(tags__title=args[1])
        else:
            try:
                year, month = args[1].split("-")
                logger.debug("分割得到的参数year:{}, month:{}".format(year, month))
                article_list = models.Article.objects.filter(user=user).filter(
                    create_time__year=year, create_time__month=month
                )
            except Exception as e:
                logger.warning("请求访问的日期归档的格式不正确!!!")
                logger.warning((str(e)))
                return HttpResponse("404")
    return render(request, "home.html",
                  {"username": username,
                   "blog": blog,
                   "article_list": article_list})


def article_detail(request, username, pk):
    """文章详情"""
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    # 找到指定的文章
    article = models.Article.objects.filter(pk=pk).first()
    # 所有评论的列表
    comment_list = models.Comment.objects.filter(article_id=pk)
    comment_count = comment_list.count()

    return render(request, "article_detail.html",
                  {"username": username,
                   "blog": blog,
                   "article": article,
                   "comment_list": comment_list,
                   "comment_count": comment_count})


def up_down(request):
    """点赞/踩"""
    is_up = json.loads(request.POST.get("is_up"))
    article_id = request.POST.get("article_id")
    user = request.user

    ret = {"status": True}
    try:
        models.ArticleUpDown.objects.create(user=user, is_up=is_up, article_id=article_id)
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        ret["status"] = False
        ret["first_action"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up

    return JsonResponse(ret)


def comment(request):
    """评论"""
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    user_pk = request.user.pk
    comment_count = request.POST.get("comment_count")

    models.Article.objects.filter(pk=article_id).update(comment_count=comment_count)

    response = {}
    if not pid:  # 根评论
        comment_obj = models.Comment.objects.create(article_id=article_id, content=content, user_id=user_pk)
    else:
        comment_obj = models.Comment.objects.create(parent_comment_id=pid,
                                                    article_id=article_id,
                                                    content=content, user_id=user_pk)

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"] = comment_obj.content
    response["username"] = comment_obj.user.username

    return JsonResponse(response)


def add_article(request):
    """发布文章"""
    if request.method == "POST":
        title = request.POST.get("title")
        article_content = request.POST.get("article_content")
        user = request.user

        bs = BeautifulSoup(article_content, "html.parser")
        desc = bs.text[0:150] + "..."

        # 过滤非法标签
        for tag in bs.find_all():
            if tag.name in ["script"]:
                tag.decompose()

        article_obj = models.Article.objects.create(title=title, user=user, desc=desc)
        models.ArticleDetail.objects.create(content=article_content, article=article_obj)
        return HttpResponse("发布成功")

    return render(request, "add_article.html")


def upload(request):
    """富文本上传文件"""
    obj = request.FILES.get("imgFile")
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", obj.name)

    with open(path, "wb") as f:
        for line in obj:
            f.write(line)

    ret = {
        "error": 0,
        "url": "/media/add_article_img/" + obj.name
    }
    return HttpResponse(json.dumps(ret))


def login(request):
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        return JsonResponse(ret)
    return render(request, "login.html")


def index(request):
    article = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article})


def register(request):
    """注册"""
    if request.method == "POST":

        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 进行验证
        if form_obj.is_valid():

            # 创建用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        # 返回错误信息
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
    form_obj = forms.RegForm()
    return render(request, "register.html", {"form_obj": form_obj})


def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    user = models.UserInfo.objects.filter(username=username)
    if user:
        ret["status"] = 1
        ret["msg"] = "用户名以存在"
    return JsonResponse(ret)


def logout(request):
    auth.logout(request)
    return redirect("/index/")


pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


