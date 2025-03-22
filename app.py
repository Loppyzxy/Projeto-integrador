import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta'  

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

def get_actor_movies(actor_id):
    url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits"
    params = {
        'api_key': 'API_KEY',
        'language': 'pt-BR' 
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()

        return data.get('cast', [])
    else:
        return []

def get_movie_data(query_params, language='pt-BR', per_page=18): 
    url = f"{BASE_URL}/discover/movie"
    query_params['api_key'] = API_KEY
    query_params['language'] = language
    query_params['page_size'] = per_page 

    try:
        response = requests.get(url, params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API: {e}")
        return None

def search_movies(query, language='pt-BR', per_page=18):
    url = f"{BASE_URL}/search/movie"
    params = {
        'api_key': API_KEY,
        'query': query,
        'language': language,
        'page_size': per_page 
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

    actor_bio = actor_data.get('biography', 'Biografia não disponível.')
    actor_birthday = actor_data.get('birthday', 'Data de nascimento não disponível.')
    actor_place_of_birth = actor_data.get('place_of_birth', 'Local de nascimento não disponível.')

    return render_template('actor_details.html', movies=actor_movies, actor=actor_data, biography=actor_bio, birthday=actor_birthday, place_of_birth=actor_place_of_birth)


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


    while len(movies) < 18:
        movies.append(None)
    movies = movies[:18] 

    return render_template('movies.html', movies=movies, total_pages=total_pages, current_page=page, genre=genre, year=year, rating=rating, language=language)

@app.before_request
def before_request():
    """Inicializa a lista de favoritos na sessão se ainda não existir."""
    if 'favorites' not in session:
        session['favorites'] = []


@app.route('/add_to_favorites/<int:movie_id>')
def add_to_favorites(movie_id):
    """Adiciona um filme à lista de favoritos na sessão."""
    favorites = session['favorites']
    if movie_id not in favorites:
        favorites.append(movie_id)
        session['favorites'] = favorites
        session.modified = True  
        flash('Filme adicionado aos favoritos!', 'success')
    else:
        flash('Este filme já está nos seus favoritos!', 'info')
    return redirect(request.referrer or url_for('movies'))  

@app.route('/remove_from_favorites/<int:movie_id>')
def remove_from_favorites(movie_id):
    """Remove um filme da lista de favoritos na sessão."""
    favorites = session['favorites']
    if movie_id in favorites:
        favorites.remove(movie_id)
        session['favorites'] = favorites
        session.modified = True
        flash('Filme removido dos favoritos.', 'success')
    else:
        flash('Este filme não está nos seus favoritos.', 'warning')
    return redirect(request.referrer or url_for('favorites'))


@app.route('/favorites')
def favorites():
    """Exibe a lista de filmes favoritos."""
    favorite_ids = session['favorites']
    movies = []
    for movie_id in favorite_ids:
        movie_data = get_movie_details(movie_id)
        if movie_data:
            movies.append(movie_data)
    return render_template('favorites.html', movies=movies)

def get_movie_details(movie_id, language='pt-BR'):
    """Busca os detalhes de um filme específico usando o ID."""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {'api_key': API_KEY, 'language': language}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar detalhes do filme: {e}")
        return None
if __name__ == '__main__':
    app.run(debug=True)