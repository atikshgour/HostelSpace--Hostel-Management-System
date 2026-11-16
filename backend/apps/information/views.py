from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response

from apps.accounts.models import AuditEvent
from apps.accounts.permissions import require
from apps.accounts.serializers import ProtectedView

from .models import Content, Rule
from .serializers import ContentSerializer, RuleSerializer


class ContentList(ProtectedView):
    def get(self, request):
        q = Content.objects.all()
        if request.user.role not in ("DIRECTOR", "CONTENT_STAFF"):
            now = timezone.now()
            q = (
                q.filter(active=True)
                .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
                .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
            )
        return self.rows(q, ContentSerializer, request)

    def post(self, request):
        require(request.user, "DIRECTOR", "CONTENT_STAFF")
        s = self.validate(ContentSerializer, request)
        s.save(updated_by=request.user)
        return Response(s.data, status=201)


class ContentDetail(ProtectedView):
    def patch(self, request, pk):
        require(request.user, "DIRECTOR", "CONTENT_STAFF")
        obj = get_object_or_404(Content, pk=pk)
        s = self.validate(ContentSerializer, request, instance=obj, partial=True)
        s.save(updated_by=request.user)
        AuditEvent.objects.create(
            actor=request.user,
            action="content_updated",
            object_key=str(pk),
            details={"fields": list(s.validated_data)},
        )
        return Response(s.data)


class Rules(ProtectedView):
    def get(self, request):
        q = (
            Rule.objects.all()
            if request.user.role in ("DIRECTOR", "CONTENT_STAFF")
            else Rule.objects.filter(active=True)
        )
        return self.rows(q, RuleSerializer, request)

    def post(self, request):
        require(request.user, "DIRECTOR", "CONTENT_STAFF")
        s = self.validate(RuleSerializer, request)
        s.save()
        return Response(s.data, status=201)


class RuleDetail(ProtectedView):
    def patch(self, request, pk):
        require(request.user, "DIRECTOR", "CONTENT_STAFF")
        s = self.validate(
            RuleSerializer,
            request,
            instance=get_object_or_404(Rule, pk=pk),
            partial=True,
        )
        s.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="rule_updated",
            object_key=str(pk),
            details={"fields": list(s.validated_data)},
        )
        return Response(s.data)
