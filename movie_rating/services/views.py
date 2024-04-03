from django.shortcuts import render, redirect
import json
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from .forms import *
from django.http import JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action
import os
from functools import wraps
#from .decorators import *

def user(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if request.session.get('user'):
            # User is authenticated, allow access to the view
            return view_func(self, request, *args, **kwargs)
        else:
            return redirect('home')
            
    return wrapper

class CustomTemplateMixin:
    renderer_classes = [TemplateHTMLRenderer]
    default_template_name = 'index.html'

    def get_template_names(self):
        action = self.action
        template_name = getattr(self, f'{action}_template_name', self.default_template_name)
        return [template_name]

class MovieViewSet(CustomTemplateMixin, viewsets.ViewSet):
    
    
    @action(detail=True, methods=['get'], url_path='list_it')
    @user
    def list_it(self, request, pk=None):
        movies = load_data(os.path.join(settings.JSON, 'movie.json'))
        print(movies)
        ratings_list = avg_ratings(movies)
        return Response({'movies': zip(movies,ratings_list)}, template_name=self.list_it_template_name)
    list_it_template_name = 'dashboard.html'
    
    
    @action(detail=True, methods=['post'], url_path='search_it')
    @user
    def search_it(self, request, pk=None):
        movie_filter = request.POST.get('filter')
        if movie_filter:
            movies = load_data(os.path.join(settings.JSON, 'movie.json'))
            matched_movies = [movie for movie in movies if movie['name'].lower() == movie_filter.lower() or  movie['genre'].lower() == movie_filter.lower() or  movie['rating'].lower() == movie_filter.lower()]
            if matched_movies:
                ratings_list = avg_ratings(matched_movies)
                return Response({'movies': zip(matched_movies,ratings_list)}, template_name=self.search_it_template_name)
            return Response({'message': 'No movies found with the given name'}, template_name=self.search_it_template_name)
        return Response({'message': 'Please provide a movie name to search'}, template_name=self.search_it_template_name)
    search_it_template_name = 'dashboard.html'
    
    
    @action(detail=True, methods=['get', 'post'], url_path='create_it')
    @user
    def create_it(self, request, pk=None):
        if request.method == 'POST':
            form = MovieForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                data['release_date'] = data['release_date'].strftime('%Y-%m-%d')
                file_path = os.path.join(settings.JSON, 'movie.json')
                movies = load_data(file_path)
                movies.append(data)
                save_data(file_path, movies)
                return JsonResponse({'message': 'Movie added successfully', 'route' : '/api/movie/None/create_it/'})
        else:
            return Response({'title': 'Add Movie', 'form': MovieForm()})
    create_it_template_name = 'forms.html'
    
    

    @action(detail=True, methods=['get', 'post'], url_path='log_in')
    def log_in(self, request, pk=None):
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                file_path = os.path.join(settings.JSON, 'user.json')
                users = load_data(file_path)
                if (data['email'],data['password']) in  [(user['email'],user['password']) for user in users]:
                    request.session['user']=[user['id'] for user in users if user['email']==data['email'] ][0]
                    return JsonResponse({'message': 'Log in successful! Visit dashboard.', 'route' : '/api/movie/None/log_in/'})
                return JsonResponse({'message': 'Incorrect credentials', 'route' : '/api/movie/None/log_in/'})
        else:
            return Response({'title': 'Log in', 'form': LoginForm()})
    log_in_template_name = 'forms.html'
        
        
    @action(detail=True, methods=['get', 'post'], url_path='register')
    def register(self, request, pk=None):
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                file_path = os.path.join(settings.JSON, 'user.json')
                users = load_data(file_path)
                if (data['email'], data['name'], data['phone']) not in [(user['email'],user['name'],user['phone']) for user in users]:
                    users.append(data)
                    save_data(file_path, users)
                    return JsonResponse({'message': 'Account successfully created. Please log in!', 'route' : '/api/movie/None/register/'})
                return JsonResponse({'message': 'Account already exists', 'route' : '/api/movie/None/register/'})
        else:
            return Response({'title': 'Register', 'form': RegisterForm()})
    register_template_name = 'forms.html'
       
     
    @action(detail=True, methods=['get', 'post'], url_path='log_out')
    @user
    def log_out(self, request, pk=None):
        if request.session.get('user'):
            del request.session['user']
        return redirect('/')
    
    
    @action(detail=True, methods=['get', 'post'], url_path='rate_it')
    @user
    def rate_it(self, request, pk=None):
        if request.method == 'POST':
            form = RatingForm(request.POST)
            if form.is_valid():
                
                file_path = os.path.join(settings.JSON, 'ratings.json')
                ratings = load_data(file_path)
                user_id = request.session['user']
                movie_id = pk
                new_id = max([rating.get('id', 0) for rating in ratings], default=0) + 1
                form.cleaned_data['id'] = new_id
                form.cleaned_data['user_id'] = user_id
                form.cleaned_data['movie_id'] = movie_id
                r = form.cleaned_data['rating']
                ratings.append(form.cleaned_data)
                save_data(file_path, ratings)
                return JsonResponse({'message': 'Thank you for rating this movie!', 'route': '/api/movie/None/register/'})
        else:
            if if_rated(request.session.get('user'), pk):
                return JsonResponse({'message': 'Already rated!', 'route': '/api/movie/None/rate_it/'})
            # Populate the hidden fields with user_id and movie_id
            form = RatingForm(initial={'user_id': request.session['user'], 'movie_id': pk})
            return Response({'title': 'Rate this Movie', 'form': form}, template_name=self.rate_it_template_name)
    rate_it_template_name = 'forms.html'
    


def home(request):
    if request.session.get('user'):
        print('hi')
        return redirect('/api/movie/None/list_it')
    return render(request, 'index.html')


def load_data(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

def save_data(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)
        
def avg_ratings(movies):
    ratings = load_data(os.path.join(settings.JSON, 'ratings.json'))
    ratings_list = []
    for movie in movies:
        l=[]
        for r in ratings:
            if r['movie_id']==movie["id"]:
                l.append(r['rating'])
                
        try:
            average_rating = round(sum(l) / len(l),1)
        except ZeroDivisionError:
            average_rating = 0
        ratings_list.append(average_rating)
    return ratings_list



def if_rated(user_id, movie_id):
    file_path = os.path.join(settings.JSON, 'ratings.json')
    ratings = load_data(file_path)
    if (user_id,movie_id) in [(rating['user_id'],rating['movie_id']) for rating in ratings]:
        return True
    return False


