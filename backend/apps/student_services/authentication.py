# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from rest_framework.authentication import SessionAuthentication


class StudentSessionAuthentication(SessionAuthentication):
    # DRF otherwise changes unauthenticated session errors to HTTP 403.
    def authenticate_header(self, request):
        return 'Session'
