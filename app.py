import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  

API_KEY = '85315830bcf4d7203721cb322ec54c68'
BASE_URL = 'https://api.themoviedb.org/3'

def get_movie_data(query_params, language='pt-BR'):
    """Busca os dados do filme com o parâmetro de idioma."""
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movies', methods=['GET'])
def movies():
    """Renderiza a página de filmes com base nos parâmetros fornecidos."""
    
    genre = request.args.get('genre')
    year = request.args.get('year')
    rating = request.args.get('rating')
    language = request.args.get('language', 'pt-BR')  
    page = request.args.get('page', 1, type=int)  

    query_params = {}

    if genre:
        query_params['with_genres'] = genre
    if year:
        query_params['primary_release_year'] = year
    if rating:
        query_params['vote_average.gte'] = rating

    
    query_params['page'] = page

    
    movie_data = get_movie_data(query_params, language)

    if movie_data is None:
        flash("Erro ao buscar filmes. Tente novamente mais tarde.", "danger")
        return redirect(url_for('index'))

    movies = movie_data.get('results', [])
    total_pages = movie_data.get('total_pages', 0)  

    
    return render_template('movies.html', movies=movies, total_pages=total_pages, current_page=page, genre=genre, year=year, rating=rating, language=language)

if __name__ == '__main__':
    app.run(debug=True)