from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import StrictSerializer


class UserInput(StrictSerializer):
    username = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)
    is_active = serializers.BooleanField(required=False)
    password = serializers.CharField(
        max_length=256, required=False, trim_whitespace=False
    )
    chief_warden = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    assigned_warden = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    srn = serializers.CharField(max_length=40, required=False)
    room = serializers.CharField(max_length=30, required=False)
    hostel = serializers.CharField(max_length=80, required=False)


class SettingInput(StrictSerializer):
    key = serializers.ChoiceField(choices=["site_title", "support_contact"])
    value = serializers.CharField(max_length=500)
