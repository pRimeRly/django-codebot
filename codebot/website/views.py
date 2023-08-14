import os
import openai

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from dotenv import load_dotenv

from .forms import SignUpForm
from .models import Code


lang_list = [
	'c', 'clike', 'cpp', 'csharp', 'css', 'dart', 'django', 'docker', 'go', 'html', 'java', 'javascript', 'markup',
	'markup-templating', 'matlab', 'mongodb', 'php', 'powershell', 'python', 'r', 'regex', 'ruby', 'rust', 'scala',
	'solidity', 'sql', 'swift', 'typescript'
]


def home(request):
	load_dotenv()
	# lang_list = ['c', 'clike', 'cpp', 'csharp', 'css', 'dart', 'django', 'docker', 'go', 'html', 'java', 'javascript', 'markup', 'markup-templating', 'matlab', 'mongodb', 'php', 'powershell', 'python', 'r', 'regex', 'ruby', 'rust', 'scala', 'solidity', 'sql', 'swift', 'typescript']

	if request.method == 'POST':
		code = request.POST['code']
		lang = request.POST['lang']

		# Check to make sure lang was picked
		if lang == "Select Programming Language":
			messages.success(request, "Hey!, You Forgot To Pick A Programming Language")
			return render(request, 'home.html', {'lang_list': lang_list, 'code': code, 'lang': lang})
		else:
			# api integration
			openai.api_key = os.getenv('OPENAI_API_KEY')

			# Create OpenAI instance
			openai.Model.list()
			# Make an OpenAI request
			try:
				response = openai.ChatCompletion.create(
					model='gpt-3.5-turbo',
					messages=[
						{"role": "system", "content": "You are a helpful assistant developer. You fix bugs in code"},
						{'role': 'user', 'content': f'Respond only with code. Fix this {lang} code: {code}'}
					],
					temperature=0,
					max_tokens=1000,
				)
				# Parse the response
				response = (response['choices'][0]['message']['content']).strip()

				# Save response to database
				record = Code(
					question=code,
					code_answer=response,
					language=lang,
					user=request.user
				)
				record.save()
				return render(request, 'home.html', {'lang_list': lang_list, 'response': response, 'lang': lang})
			except Exception as e:
				return render(request, 'home.html', {'lang_list': lang_list, 'response': e, 'lang': lang})

	return render(request, 'home.html', {'lang_list': lang_list})


def suggest(request):
	load_dotenv()
	# lang_list = ['c', 'clike', 'cpp', 'csharp', 'css', 'dart', 'django', 'docker', 'go', 'html', 'java', 'javascript', 'markup', 'markup-templating', 'matlab', 'mongodb', 'php', 'powershell', 'python', 'r', 'regex', 'ruby', 'rust', 'scala', 'solidity', 'sql', 'swift', 'typescript']

	if request.method == 'POST':
		code = request.POST['code']
		lang = request.POST['lang']

		# Check to make sure lang was picked
		if lang == "Select Programming Language":
			messages.success(request, "Hey!, You Forgot To Pick A Programming Language")
			return render(request, 'suggest.html', {'lang_list': lang_list, 'code': code, 'lang': lang})
		else:
			# api integration
			openai.api_key = os.getenv('OPENAI_API_KEY')

			# Create OpenAI instance
			openai.Model.list()
			# Make an OpenAI request
			try:
				response = openai.ChatCompletion.create(
					model='gpt-3.5-turbo',
					messages=[
						{"role": "system", "content": "You are a helpful assistant developer. You only respond with code, no explanation."},
						{'role': 'user', 'content': f'{code}, Respond only with the code.'}
					],
					temperature=0,
					max_tokens=1000,
				)
				# Parse the response
				response = (response['choices'][0]['message']['content']).strip()

				# Save response to database
				record = Code(
					question=code,
					code_answer=response,
					language=lang,
					user=request.user
				)
				record.save()
				return render(request, 'suggest.html', {'lang_list': lang_list, 'response': response, 'lang': lang})
			except Exception as e:
				return render(request, 'suggest.html', {'lang_list': lang_list, 'response': e, 'lang': lang})

	return render(request, 'suggest.html', {'lang_list': lang_list})


def login_user(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, 'Login successful.')
			return redirect('home')
		else:
			messages.success(request, 'Error Logging In. Please try again.')
			return redirect('home')
	else:
		return render(request, 'home.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, 'You Have Been Logged Out.')
	return redirect('home')


def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)

			messages.success(request, "You Have Registered Successfully!")
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'register.html', {"form": form})


def history(request):
	if request.user.is_authenticated:
		code = Code.objects.filter(user_id=request.user.id)
		return render(request, 'history.html', {"code_history": code})
	else:
		messages.success(request, "You Are Not Authenticated To View History Page")
		return redirect('home')


def delete_history(request, history_id):
	past = Code.objects.get(pk=history_id)
	past.delete()
	messages.success(request, "Deleted Successfully")
	return redirect('history')
