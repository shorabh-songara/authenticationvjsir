from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
   return HttpResponse("<h1>hey this is a success page</h1>")




def success_page(request):
    print("*" * 10)
    return HttpResponse("<h1>hey this is a success page</h1>")