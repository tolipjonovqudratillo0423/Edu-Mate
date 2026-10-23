from django.shortcuts import redirect

def redirector(request):
    return redirect("swagger-ui")