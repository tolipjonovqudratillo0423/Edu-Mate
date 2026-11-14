# EduMate — project rules
Stack: Django + DRF, JWT auth, custom User (email login) + Profile, SQLite (dev).
Apps: edumate/apps/{authentication, catalog, common, goals, matching, users}.

Architecture (strict):
- repositories.py: ORM access only. No business rules, no DRF imports.
- services.py: business rules + validation. Views call services only,
  services call repositories only. Raise DRF exceptions
  (NotFound, ValidationError, PermissionDenied).
- serializers.py: ModelSerializer, field-level validation only.
- views.py: APIView only, thin: serializer -> service -> Response.
- Reusable permission classes live in apps/common/permissions.py.
- urls.py per app, included from edumate/urls.py.
- tests.py: APITestCase, force_authenticate, reverse() names. Cover success,
  validation errors, permission denied, anonymous.

Working rules:
- Read existing code (users app first) and match its style.
- Do not edit existing models or migrations unless the task says so.
  If a model change is needed, stop and ask.
- No new dependencies.
- If anything is ambiguous, ask. Do not guess.
- ONE task per run. Show a short plan (files to create/change) and wait for my approval before coding.
- Finish by running `python manage.py test <app>`, report the result, and
  list every file changed.
- After the code, give me 3 questions that check whether I understood it.