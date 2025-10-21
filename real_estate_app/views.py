from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <h1>👁‍🗨💬💯🏢 Midas CRM</h1>
    <p>Добро пожаловать, тут можно заработать</p>
    <p><a href="/admin/">Войти</a></p>
    """)