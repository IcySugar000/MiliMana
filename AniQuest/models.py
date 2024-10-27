from django.db import models


class Bangumi(models.Model):
    """
    番剧
    name：番剧名称
    rss：番剧rss订阅链接
    re_rule：用于下载时筛选的正则表达式，决定了哪些种子需要被下载
    bgm_id：对应的bgm.tv网站的番剧id
    archived：是否归档，已归档则不用检测下载
    """
    name = models.CharField(max_length=400)
    rss = models.CharField(max_length=600)
    re_rule = models.CharField(max_length=600, blank=True)
    bgm_id = models.IntegerField(default=0)
    archived = models.BooleanField(default=False)
    poster = models.ImageField(upload_to='posters', max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Record(models.Model):
    """
    下载记录
    bangumi：下载的番剧，多对一关联Bangumi
    file_name：下载的文件名
    have_downloaded：是否已经下载，当某文件被检测到且不符合Rule的时候设置为False，被检测到且已经下载则为True
    download_time：下载时间
    scrapped: 是否已被挂削元信息
    """
    bangumi = models.ForeignKey(Bangumi, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=260)
    have_downloaded = models.BooleanField(default=False)
    download_time = models.DateTimeField()

    def __str__(self):
        return f"{self.file_name} at {self.download_time}"


class Episode(models.Model):
    """
    集数记录
    bangumi: 对应番剧
    file_name: 对应文件名
    scrapped: 是否已经挂削元信息
    """
    bangumi = models.ForeignKey(Bangumi, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=260, default="")
    scrapped = models.BooleanField(default=False)
