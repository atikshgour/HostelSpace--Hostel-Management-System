# Owner: Atiksh Gour | US-13,US-14,US-15,US-16 | Dev sprint 2; 3 | SRS sprint 4; 5 | Reviewer: Anvi Srinivas (pending)
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.models import AuditEvent
from apps.accounts.permissions import require
from apps.accounts.serializers import ProtectedView

from . import payments, services
from .models import (
    Complaint,
    ComplaintTransition,
    Coupon,
    FeeDue,
    MessAllocation,
    MessChoiceEvent,
    MessOption,
    PaymentAttempt,
)
from .serializers import (
    AssignInput,
    AttemptSerializer,
    ComplaintInput,
    ComplaintSerializer,
    CouponSerializer,
    FeeSerializer,
    InitiateInput,
    MessChoiceSerializer,
    MessOptionSerializer,
    MessSelectInput,
    MessSerializer,
    ProgressInput,
    SimulateInput,
    VerifyInput,
)


def complaint_scope(user):
    q = Complaint.objects.prefetch_related("transitions")
    if user.role == "STUDENT":
        return q.filter(student=user)
    if user.role == "MAINTENANCE_STAFF":
        return q.filter(assigned_to=user)
    if user.role == "DIRECTOR":
        return q
    require(user, "STUDENT", "MAINTENANCE_STAFF", "DIRECTOR")


class Complaints(ProtectedView):
    def get(self, request):
        return self.rows(complaint_scope(request.user), ComplaintSerializer, request)

    def post(self, request):
        s = self.validate(ComplaintInput, request)
        return Response(
            ComplaintSerializer(
                services.submit_complaint(request.user, s.validated_data)
            ).data,
            status=201,
        )


class ComplaintDetail(ProtectedView):
    def get(self, request, pk):
        return Response(
            ComplaintSerializer(
                get_object_or_404(complaint_scope(request.user), pk=pk)
            ).data
        )


class ComplaintAssign(ProtectedView):
    @transaction.atomic
    def post(self, request, pk):
        require(request.user, "DIRECTOR")
        s = self.validate(AssignInput, request)
        obj = get_object_or_404(
            complaint_scope(request.user).select_for_update(), pk=pk
        )
        if obj.status == "Resolved":
            raise ValidationError("Resolved complaints cannot be reassigned.")
        obj.assigned_to = s.validated_data["assigned_to"]
        obj.save(update_fields=["assigned_to"])
        ComplaintTransition.objects.create(
            complaint=obj,
            actor=request.user,
            from_status=obj.status,
            to_status=obj.status,
            remarks=f"Assigned to {obj.assigned_to.username}",
        )
        return Response(ComplaintSerializer(obj).data)


class ComplaintProgress(ProtectedView):
    def post(self, request, pk):
        s = self.validate(ProgressInput, request)
        return Response(
            ComplaintSerializer(
                services.progress(request.user, pk, **s.validated_data)
            ).data
        )


class Mess(ProtectedView):
    def get(self, request):
        require(request.user, "STUDENT", "MESS_STAFF", "DIRECTOR")
        q = MessAllocation.objects.select_related("student").order_by("student_id")
        if request.user.role == "STUDENT":
            q = q.filter(student=request.user)
        if request.user.role == "WARDEN":
            q = q.filter(student__student_profile__assigned_warden=request.user)
        return self.rows(q, MessSerializer, request)

    def post(self, request):
        require(request.user, "MESS_STAFF")
        raise ValidationError(
            "Select an available mess through /api/mess/select/ instead of entering free text."
        )


class Coupons(ProtectedView):
    def get(self, request):
        require(request.user, "STUDENT", "MESS_STAFF", "DIRECTOR")
        q = Coupon.objects.order_by("-pk")
        if request.user.role == "STUDENT":
            q = q.filter(
                student=request.user,
                active=True,
                valid_from__lte=timezone.localdate(),
                valid_to__gte=timezone.localdate(),
            )
        if request.user.role == "WARDEN":
            q = q.filter(student__student_profile__assigned_warden=request.user)
        return self.rows(q, CouponSerializer, request)

    def post(self, request):
        require(request.user, "MESS_STAFF")
        s = self.validate(CouponSerializer, request)
        check_student_scope(request.user, s.validated_data["student"])
        s.save(created_by=request.user)
        return Response(s.data, status=201)


class CouponDetail(ProtectedView):
    def patch(self, request, pk):
        require(request.user, "MESS_STAFF")
        obj = get_object_or_404(Coupon, pk=pk)
        check_student_scope(request.user, obj.student)
        s = self.validate(CouponSerializer, request, instance=obj, partial=True)
        if "student" in s.validated_data:
            check_student_scope(request.user, s.validated_data["student"])
        s.save()
        return Response(s.data)


class Fees(ProtectedView):
    def get(self, request):
        require(request.user, "STUDENT", "DIRECTOR")
        q = FeeDue.objects.all()
        if request.user.role == "STUDENT":
            q = q.filter(student=request.user)
        if request.user.role == "WARDEN":
            q = q.filter(student__student_profile__assigned_warden=request.user)
        return self.rows(q, FeeSerializer, request)

    def post(self, request):
        require(request.user, "DIRECTOR")
        s = self.validate(FeeSerializer, request)
        check_student_scope(request.user, s.validated_data["student"])
        s.save()
        return Response(s.data, status=201)


class Attempts(ProtectedView):
    def get(self, request):
        require(request.user, "STUDENT", "DIRECTOR")
        q = PaymentAttempt.objects.order_by("-created_at")
        if request.user.role == "STUDENT":
            q = q.filter(fee__student=request.user)
        if request.user.role == "WARDEN":
            q = q.filter(fee__student__student_profile__assigned_warden=request.user)
        return self.rows(q, AttemptSerializer, request)


class Initiate(ProtectedView):
    def post(self, request):
        require(request.user, "STUDENT")
        s = self.validate(InitiateInput, request)
        a = payments.initiate(request.user, s.validated_data["fee"])
        data = AttemptSerializer(a).data
        data["checkout_key"] = (
            settings.RAZORPAY_KEY_ID if a.provider == "razorpay" else ""
        )
        data["simulation_label"] = (
            "LOCAL SIMULATION — NO REAL PAYMENT" if a.provider == "simulation" else ""
        )
        return Response(data, status=201)


class Verify(ProtectedView):
    def post(self, request):
        require(request.user, "STUDENT")
        s = self.validate(VerifyInput, request)
        return Response(
            AttemptSerializer(payments.verify(request.user, **s.validated_data)).data
        )


class Simulate(ProtectedView):
    def post(self, request):
        require(request.user, "STUDENT")
        s = self.validate(SimulateInput, request)
        return Response(
            AttemptSerializer(payments.simulate(request.user, **s.validated_data)).data
        )


def check_student_scope(actor, student):
    from rest_framework.exceptions import PermissionDenied

    if (
        actor.role == "WARDEN"
        and getattr(
            getattr(student, "student_profile", None), "assigned_warden_id", None
        )
        != actor.pk
    ):
        raise PermissionDenied("This student is not assigned to you.")


class MessOptions(ProtectedView):
    def get(self, request):
        from django.db.models import Count, Q

        require(request.user, "STUDENT", "DIRECTOR", "MESS_STAFF")
        q = MessOption.objects.annotate(
            enrolled=Count(
                "allocations", filter=Q(allocations__student__is_active=True)
            )
        )
        if request.user.role == "STUDENT":
            q = q.filter(active=True)
        return self.rows(q.order_by("name", "pk"), MessOptionSerializer, request)

    def post(self, request):
        require(request.user, "MESS_STAFF")
        s = self.validate(MessOptionSerializer, request)
        s.save()
        return Response(s.data, status=201)


class MessOptionDetail(ProtectedView):
    @transaction.atomic
    def patch(self, request, pk):
        require(request.user, "MESS_STAFF")
        obj = get_object_or_404(MessOption.objects.select_for_update(), pk=pk)
        s = self.validate(MessOptionSerializer, request, instance=obj, partial=True)
        if (
            "name" in s.validated_data
            and s.validated_data["name"] != obj.name
            and obj.allocations.exists()
        ):
            raise ValidationError(
                {
                    "name": "An enrolled mess cannot be renamed; deactivate it and create another."
                }
            )
        if (
            s.validated_data.get("capacity", obj.capacity)
            < obj.allocations.filter(student__is_active=True).count()
        ):
            raise ValidationError(
                {"capacity": "Capacity cannot be lower than current enrolment."}
            )
        s.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="mess_option_updated",
            object_key=str(pk),
            details={"fields": list(s.validated_data)},
        )
        return Response(s.data)


class MessSelect(ProtectedView):
    def post(self, request):
        require(request.user, "MESS_STAFF")
        s = self.validate(MessSelectInput, request)
        return Response(
            MessSerializer(services.select_mess(request.user, **s.validated_data)).data
        )


class MessHistory(ProtectedView):
    def get(self, request):
        require(request.user, "STUDENT", "DIRECTOR", "MESS_STAFF")
        q = MessChoiceEvent.objects.all()
        if request.user.role == "STUDENT":
            q = q.filter(student=request.user)
        if request.user.role == "WARDEN":
            q = q.filter(student__student_profile__assigned_warden=request.user)
        return self.rows(q, MessChoiceSerializer, request)
