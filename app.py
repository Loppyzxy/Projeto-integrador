import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

API_KEY = '85315830bcf4d7203721cb322ec54c68'
BASE_URL = 'https://api.themoviedb.org/3'

def search_actors(query, language='pt-BR'):
    url = f"{BASE_URL}/search/person"
    params = {
        'api_key': API_KEY,
        'query': query,
        'language': language
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()  
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar atores: {e}")
        return {'results': []}  

def get_actor_movies(actor_id, language='pt-BR'):
    url = f"{BASE_URL}/person/{actor_id}/movie_credits"
    params = {'api_key': API_KEY, 'language': language}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('cast', [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar filmes do ator: {e}")
        return []

def get_movie_data(query_params, language='pt-BR'):
    url = f"{BASE_URL}/discover/movie"
    query_params['api_key'] = API_KEY
    query_params['language'] = language

    try:
        response = requests.get(url, params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API: {e}")
        return None

def search_movies(query, language='pt-BR'):
    url = f"{BASE_URL}/search/movie"
    params = {
        'api_key': API_KEY,
        'query': query,
        'language': language
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar filmes: {e}")
        return None

def get_genres():
    url = f"{BASE_URL}/genre/movie/list"
    params = {'api_key': API_KEY, 'language': 'pt-BR'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('genres', [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar gêneros: {e}")
        return []

def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {'api_key': API_KEY, 'language': 'pt-BR'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        video_data = response.json()
        if video_data['results']:
            return video_data['results'][0]['key']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar trailer: {e}")
        return None


@app.route('/actors', methods=['GET'])
def actors():
    query = request.args.get('query')
    actors_data = {'results': []}  
    if query:
        actors_data = search_actors(query)
    return render_template('actors.html', actors=actors_data.get('results', []))

@app.route('/actor/<int:actor_id>', methods=['GET'])
def actor_details(actor_id):
    actor_movies = get_actor_movies(actor_id)
    
    url = f"{BASE_URL}/person/{actor_id}"
    params = {'api_key': API_KEY, 'language': 'pt-BR'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        actor_data = response.json()  
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar detalhes do ator: {e}")
        actor_data = {}

    return render_template('actor_details.html', movies=actor_movies, actor=actor_data)


@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/')
def index():
    genres = get_genres()
    return render_template('index.html', genres=genres)

@app.route('/movies', methods=['GET'])
def movies():
    query = request.args.get('query')  
    genre = request.args.get('genre')
    year = request.args.get('year')
    rating = request.args.get('rating')
    language = request.args.get('language', 'pt-BR')
    page = request.args.get('page', 1, type=int)

    query_params = {}

    if query:
        query_params['query'] = query
    if genre:
        query_params['with_genres'] = genre
    if year:
        query_params['primary_release_year'] = year
    if rating:
        query_params['vote_average.gte'] = rating

    query_params['page'] = page

    if query:
        
        movie_data = search_movies(query, language)
    else:
        
        movie_data = get_movie_data(query_params, language)

    if movie_data is None:
        flash("Erro ao buscar filmes. Tente novamente mais tarde.", "danger")
        return redirect(url_for('index'))

    movies = movie_data.get('results', [])
    total_pages = movie_data.get('total_pages', 0)

    for movie in movies:
        trailer_key = get_trailer(movie['id'])
        movie['trailer_key'] = trailer_key

    return render_template('movies.html', movies=movies, total_pages=total_pages, current_page=page, genre=genre, year=year, rating=rating, language=language)

if __name__ == '__main__':
    app.run(debug=True)