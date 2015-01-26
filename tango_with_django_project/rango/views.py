from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there world! <br/> <a href='/rango/about'>About</a>")

def about(request):
    return HttpResponse("This tutorial has been put together by Ross Anderson,2071174 <br/> <a href='/rango'>Index</a>")
