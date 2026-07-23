from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .agent import run_agent
import json


@login_required(login_url='/users/login/')
def agent_home(request):
    return render(request, 'chatbot/agent.html')


@login_required(login_url='/users/login/')
def agent_plan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    data = json.loads(request.body)
    goal = data.get('goal', '').strip()

    if not goal:
        return JsonResponse({'error': 'Please provide a goal'}, status=400)

    result = run_agent(goal)
    return JsonResponse(result)