from django.shortcuts import render, redirect
from django.http import JsonResponse
from openai import OpenAI


from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
import os
import json
from django.conf import settings

API_KEY = str(settings.OPENAI_API_KEY)

client = OpenAI(api_key=API_KEY)

# context = "Instruction :You are Recipe master you know everything and all about the recipes, You are a helpful assistant. Explicitly give [protein,fat,carbs,kcals,ingredients] dont give extra response give exact number only, EXACT NUMBERS ONLY when you give result protein,fat,carbs,kcals please give only number nothing else no units no keywords please like ""Approximately"" or ""nearly"" etc, in response You are a human. Instruction :You are Recipe master you know everything and all about the recipes Instruction: give response in only that schema nothing more, give ingredients properly like quantity  and whole output should be json hence containing key and value"
context = "As a Carbon Calculator tool, I facilitate the assessment of carbon footprints for various modes of transportation between two locations. Users can input details such as starting point, destination, and transportation method (car, bus, train, airplane) to generate an estimate of carbon emissions. This tool aims to promote environmental awareness and encourage users to make informed choices regarding their travel options. Return data in JSON TYPE"
def ask_openai(message):
    response = client.chat.completions.create(model = "gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": message},
    ])
    print(response)
    answer = response.choices[0].message.content.strip()
    # try:
    #     # Parse the JSON string into a Python dictionary
    #     answer_data = json.loads(answer)
    # except json.JSONDecodeError:
    #     # If JSON decoding fails, handle it appropriately
    #     answer_data = {"error": "The response from the AI was not in the expected format."}

    return answer


# Test the function
# user_message = "Tell me about the solar system."
# bot_response = ask_openai(user_message)
# print("Bot's response:", bot_response)

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response_data = ask_openai(message)

        # if "error" in response_data:
        #     # If there's an error in the response_data, return it as the response
        #     structured_response = response_data["error"]
        # else:
        #     # Format the response as structured content
        #     # structured_response = "Nutrition Values\n"
        #     # structured_response += f"Protein: {response_data.get('protein', 'N/A')} g, "
        #     # structured_response += f"Fat: {response_data.get('fat', 'N/A')} g, "
        #     # structured_response += f"Carbs: {response_data.get('carbs', 'N/A')} g, "
        #     # structured_response += f"Kcals: {response_data.get('kcals', 'N/A')} Kcals\n\n"
        #     # structured_response += "Ingredients\n"
        #     # for ingredient in response_data.get('ingredients', []):
        #     #     structured_response += f"- {ingredient}\n"
        #     pass

        # Create chat object and save
        chat = Chat(user=request.user, message=message, response=response_data, created_at=timezone.now())
        chat.save()

        # Return the response as JSON and also structure_response should also be a json in it self
        # return JsonResponse({'message': message, 'response': json.dumps(structured_response)})

        return JsonResponse({'message': message, 'response': response_data})
    return render(request, 'chatbot.html', {'chats': chats})



def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')