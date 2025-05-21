import json
from .models import AuditLog

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ne logger que les appels API
        if request.path.startswith('/api/'):
            user = getattr(request, 'user', None)

            # Gestion intelligente du contenu
            try:
                if request.method == 'GET':
                    body = json.dumps(dict(request.GET))
                elif request.body:
                    body = request.body.decode('utf-8')
                else:
                    body = ''
            except:
                body = '[unreadable or already consumed]'

            # Troncature si trop gros
            if len(body) > 500:
                body = body[:500] + '...'

            AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                method=request.method,
                path=request.path,
                body=body
            )

        return response
