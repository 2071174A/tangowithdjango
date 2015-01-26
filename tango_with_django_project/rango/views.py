from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    hi = 1
    return HttpResponse("Rango says hey there world!")

# Create your views here.
