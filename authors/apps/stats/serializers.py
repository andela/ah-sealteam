from django.db.models import Sum
from rest_framework import serializers

from authors.apps.articles.models import Article
from authors.apps.articles.serializers import ArticleSerializer, \
    TaggedOjectRelatedField
from authors.apps.stats.models import ReadingStatistics


class ReadingStatisticsSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()

    class Meta:
        model = ReadingStatistics

        fields = (
            'read_last_at',
            'no_read',
            'article'
        )

    def get_article(self, obj):
        serializer = ArticleSerializer(obj.article)
        serializer.data.pop('body')
        return serializer.data


class MyArticleStacsSerializer(serializers.ModelSerializer):
    tags = TaggedOjectRelatedField(many=True)
    reads = serializers.SerializerMethodField('reads_no')

    class Meta:
        model = Article
        fields = (
            'slug',
            'title',
            'description',
            'tags',
            'createdAt',
            'updatedAt',
            'body',
            'read_time',
            'reads'
        )

    def reads_no(self, obj):
        sum_reads = obj.article_read.filter(article_id=obj.pk).aggregate(
            Sum('no_read'))
        try:
            latest_date = obj.article_read.filter(article_id=obj.pk).latest(
                "read_last_at").read_last_at
        except ReadingStatistics.DoesNotExist:
            latest_date = None
        sum_reads = 0 if not sum_reads["no_read__sum"] else sum_reads[
            "no_read__sum"]
        return {
            "no_read": sum_reads,
            "read_last_at": latest_date
        }
