# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from collections.abc import Mapping

from rest_framework import serializers

from .models import Complaint, ComplaintCategory, ComplaintTransition


class ComplaintCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCategory
        fields = ['id', 'code', 'name']
        read_only_fields = fields


class ComplaintSubmissionSerializer(serializers.Serializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ComplaintCategory.objects.filter(is_active=True),
        pk_field=serializers.IntegerField(min_value=1),
    )
    description = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            unexpected = set(data) - set(self.fields)
            if unexpected:
                raise serializers.ValidationError({
                    key: ['This field is not accepted.'] for key in sorted(unexpected)
                })
            if 'description' in data and not isinstance(data['description'], str):
                raise serializers.ValidationError({'description': ['Expected a string.']})
        return super().to_internal_value(data)


class ComplaintTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintTransition
        fields = ['id', 'actor', 'created_at', 'old_status', 'new_status', 'remarks']
        read_only_fields = fields


class ComplaintSerializer(serializers.ModelSerializer):
    category_code = serializers.CharField(source='category.code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    history = ComplaintTransitionSerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id', 'room', 'category', 'category_code', 'category_name',
            'description', 'status', 'created_at', 'history',
        ]
        read_only_fields = fields
