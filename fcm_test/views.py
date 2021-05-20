from django.http import HttpResponse

def home(request):
    host = request.META['HTTP_HOST']
    str = f"You can go to [{host}/api] ,[{host}/api-auth],[{host}/admin]"
    return HttpResponse(str)