from rest_framework import serializers

from apps.accounts.serializers import StrictModelSerializer

from .models import Content, Rule


class ContentSerializer(StrictModelSerializer):
    class Meta:
        model = Content
        fields = [
            "id",
            "kind",
            "title",
            "body",
            "active",
            "starts_at",
            "ends_at",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_by", "updated_at"]

    def validate(self, data):
        a = data.get("starts_at", getattr(self.instance, "starts_at", None))
        b = data.get("ends_at", getattr(self.instance, "ends_at", None))
        if a and b and b < a:
            raise serializers.ValidationError({"ends_at": "End must follow start."})
        return data


class RuleSerializer(StrictModelSerializer):
    weightage = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = Rule
        fields = ["id", "title", "body", "weightage", "active"]
        read_only_fields = ["id"]
