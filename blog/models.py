from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """用户信息表"""
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to="avatars/",
                              default="avatars/default.png",
                              verbose_name="头像")
    create_time = models.DateTimeField(auto_now_add=True)

    blog = models.OneToOneField(to="Blog", to_field="nid", null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "用户"


class Blog(models.Model):
    """博客信息"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)  # 个人博客标题
    site = models.CharField(max_length=32, unique=True)  # 个人博客后缀
    theme = models.CharField(max_length=32)  # 博客主题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "blog站点"


class Category(models.Model):
    """个人博客文章分类"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 分类标题
    # 外键关联博客,一个博客站点可以有多个分类
    blog = models.ForeignKey(to="Blog", to_field="nid")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "文章分类"


class Tag(models.Model):
    """标签表"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 标签名
    blog = models.ForeignKey(to="Blog", to_field="nid")  # 所属博客

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "标签"


class Article(models.Model):
    """文章表"""
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)  # 文章标题
    desc = models.CharField(max_length=255)  # 简介
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间

    comment_count = models.IntegerField(verbose_name="评论数", default=0)
    up_count = models.IntegerField(verbose_name="点赞数", default=0)
    down_count = models.IntegerField(verbose_name="踩数", default=0)

    # 关联分类表
    category = models.ForeignKey(to="Category", to_field="nid", null=True)
    # 关联用户信息表
    user = models.ForeignKey(to="UserInfo", to_field="nid")
    # 关联标签表
    tags = models.ManyToManyField(to="Tag", through="Article2Tag",
                                  through_fields=("article", "tag"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "文章"


class ArticleDetail(models.Model):
    """文章详情表"""
    nid = models.AutoField(primary_key=True)
    content = models.TextField()
    article = models.OneToOneField(to="Article", to_field="nid")  # 文章

    class Meta:
        verbose_name_plural = "文章详情"


class Article2Tag(models.Model):
    """文章和标签的多对多关系表"""
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid")  # 文章
    tag = models.ForeignKey(to="Tag", to_field="nid")  # 标签

    def __str__(self):
        return "{}-{}".format(self.article, self.tag)

    class Meta:
        unique_together = (("article", "tag"),)
        verbose_name_plural = "文章-标签"


class ArticleUpDown(models.Model):
    """点赞表"""
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to="UserInfo", null=True)  # 用户
    article = models.ForeignKey(to="Article", null=True)  # 文章
    is_up = models.BooleanField(default=True)  # 赞/踩

    class Meta:
        unique_together = (("article", "user"),)
        verbose_name_plural = "文章点赞"


class Comment(models.Model):
    """评论表"""
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid")  # 文章
    user = models.ForeignKey(to="UserInfo", to_field="nid")  # 用户
    content = models.CharField(max_length=255)  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey("self", null=True, blank=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name_plural = "评论"

