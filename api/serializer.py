from rest_framework import serializers
from rect.models import Rect, OColumn, PageRect


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        fields = ('cncode', 'w', 'cn', 'word', 'wcc', 'op', 'cc',
                  'x', 'id', 'ts', 'ln', 'h', 'y')


class OColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OColumn
        fields = ('s3_uri', 'code', 'x', 'y')


class PageRectSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRect
        fields = ('id', 's3_uri', 'code', 'json_rects', 'column_count')
