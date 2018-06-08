from django.http import HttpResponse


def health_view(request):
    return HttpResponse('ok', content_type="text/plain")
