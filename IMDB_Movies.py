from flask import Flask, request,jsonify
from py2neo import Graph, Node, Relationship
import csv
from neo4j import GraphDatabase


app = Flask(__name__)

url = "bolt://localhost:7687/"
usr="neo4j"
pwd="Admin1234"
graph = Graph(url, auth = (usr,pwd))

# Add all the movies from the CSV file to the Neo4j database
@app.route('/imdb/addall', methods=['GET'])
def add_all_movies():
    try:
        with open('IMDB-Movie-Data.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                
                if(row['Revenue'] == ''):
                    movie = Node("Movie", ids=row.get('Ids', None), title=row.get('Title').strip(), description=row.get('Description', None), year=row.get('Year', None), runtime=row.get('Runtime', None), rating=row.get('Rating', None), votes=row.get('Votes', None))
                else:
                    movie = Node("Movie", ids=row.get('Ids', None), title=row.get('Title').strip(), description=row.get('Description', None), year=row.get('Year', None), runtime=row.get('Runtime', None), rating=row.get('Rating', None), votes=row.get('Votes', None) , revenue=row.get('Revenue', None))
                
                graph.merge(movie, "Movie", "ids")
                
                genres = row['Genre'].split(',')
                for genre in genres:
                    genre_node = Node("Genre", name=genre.strip())
                    in_genre = Relationship(movie, "IN", genre_node)
                    graph.merge(in_genre, "Genre", "name")
                    
                actors = row['Actors'].split(',')
                for actor in actors:
                    actor_node = Node("Person", name=actor.strip())
                    acted_in = Relationship(actor_node, "ACTED_IN", movie)
                    graph.merge(acted_in, "Person", "name")
                
                director_node = Node("Person", name=row['Director'].strip())
                directed = Relationship(director_node, "DIRECTED", movie)
                graph.merge(directed, "Person", "name")

        return jsonify({"message": "All movies added successfully"}), 200
    
    except Exception as ex:
        return jsonify({"message": "Error occured while adding the movies data from csv"}), 500
     
# Delete all the movies from the Neo4j database
@app.route('/imdb/deleteall', methods=['GET'])
def delete_all_movies():
    try:
        deleteQuery = """MATCH (n) DETACH DELETE n"""
        graph.run(deleteQuery)
        return jsonify({"message": "All movies deleted"}), 200
    except Exception as ex:
        return jsonify({"message": "Error occured while deleting all movies"}), 500


#1. Insert the new movie information
@app.route('/imdb', methods=['POST'])
def post_movie_data():
    try:
        movie_data = request.get_json()
        actors = movie_data['actors'].split(',')
        genres = movie_data['genres'].split(',')
        directors = movie_data['directors'].split(',')
        
        movie = Node("Movie", ids=movie_data.get('ids', None), title=movie_data.get('title').strip(), description=movie_data.get('description', None), year=movie_data.get('year', None), runtime=movie_data.get('runtime', None), rating=movie_data.get('rating', None), votes=movie_data.get('votes', None) , revenue=movie_data.get('revenue', None))
        
        graph.merge(movie, "Movie", "title")
        
        for genre in genres:
            genre_node = Node("Genre", name=genre.strip())
            in_genre = Relationship(movie, "IN", genre_node)
            graph.merge(in_genre, "Genre", "name")
            
        for actor in actors:
            actor_node = Node("Person", name=actor.strip())
            acted_in = Relationship(actor_node, "ACTED_IN", movie)
            graph.merge(acted_in, "Person", "name")
        
        for director in directors:
            director_node = Node("Person", name=director.strip())
            directed = Relationship(director_node, "DIRECTED", movie)
            graph.merge(directed, "Person", "name")


        checkQuery = """MATCH (m:Movie{title:$movie_title}) RETURN m AS Movie"""
        result = graph.run(checkQuery, movie_title=movie_data['title']).data()
        
        if result:
            return jsonify({"message": "Movie inserted successfully"}), 201
        else:
            return jsonify({"message": "Movie didnt get inserted"}), 404
        
    except Exception as ex:
        return jsonify({"message": "Error occured while inserting the movie data"}), 500


#2.	Update the movie information using title. (By update only title, description, and rating)
@app.route('/imdb/<string:fname>', methods=['PATCH'])
def update_movie_data(fname):
    try:
        movie_data = request.get_json()
        checkMovieQuery = """MATCH (m:Movie{title:$movie_title}) RETURN m AS Movie"""
        result = graph.run(checkMovieQuery, movie_title=fname).data()
        
        if not result:
            return jsonify({"message": "Movie: '"+fname+"' not found"}), 404
        else:
            updateQuery = """MATCH (m:Movie{title:$movie_title})"""
            if 'title' in movie_data:
                updateQuery += " SET m.title = $title"
            if 'description' in movie_data:
                updateQuery += " SET m.description = $description"
            if 'rating' in movie_data:
                updateQuery += " SET m.rating = $rating"
            graph.run(updateQuery, movie_title=fname, title=movie_data.get('title', None), description=movie_data.get('description', None), rating=movie_data.get('rating', None))
            
            
            checkQuery = """MATCH (m:Movie{title:$movie_title}) RETURN m AS Movie"""
            result = graph.run(checkQuery, movie_title=movie_data.get('title',fname)).data()
            
            if result:
                return jsonify({"message": "Movie successfully updated"}), 200
            else:
                return jsonify({"message": "Movie: '"+fname+"' not found"}), 404
    except Exception as ex:
        return jsonify({"message": "Error occured while updating the movie"}), 500
    

# 3. Delete the movie information using title.
@app.route('/imdb/<string:fname>', methods=['DELETE'])
def delete_movie(fname):
    try:
        checkQuery = """MATCH (m:Movie{title:$movie_title}) RETURN m"""
        result = graph.run(checkQuery, movie_title=fname).data()
        
        if not result:
            return jsonify({"message": "Movie: '"+fname+"' not found"}), 404
        else:
            deletemovieQuery = """MATCH (m:Movie{title:$movie_title}) DETACH DELETE m"""
            graph.run(deletemovieQuery, movie_title=fname)
            
            checkQuery = """MATCH (m:Movie{title:$movie_title}) RETURN m"""
            result = graph.run(checkQuery, movie_title=fname).data()
            
            if not result:
                return jsonify({"message": "Movie: '"+fname+"' got deleted successfully"}), 200
            else:
                return jsonify({"message": "Movie: '"+fname+"' not found"}), 404
            
    except Exception as ex:
        return jsonify({"message": "Error occured while deleting the movie: "+fname}), 500



# 4. Retrieve all the movies in database.
@app.route('/imdb', methods=['GET'])
def get_movies():
    try:
        allmoviesQuery = """MATCH (m:Movie) RETURN m as Movie"""
        result = graph.run(allmoviesQuery).data()    
        if result:
            return jsonify(result),200
        else:
            return jsonify({"message": "No Movies found"}), 404
    except Exception as ex:
        return jsonify({"message": "Error occured while fetching all movies"}), 500



# 5. Display the movie’s details includes actors, directors and genres using title.
@app.route('/imdb/<string:fname>', methods=['GET'])
def get_movie(fname):
    try:
        movieDataQuery = """MATCH (m:Movie{title:$movie_title})
        OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
        OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
        OPTIONAL MATCH (m)-[:IN]->(g:Genre)
        RETURN m AS Movie, COLLECT(DISTINCT a) AS Actors, COLLECT(DISTINCT d) AS Directors, COLLECT(DISTINCT g) AS Genres;"""
        result = graph.run(movieDataQuery, movie_title=fname).data()
        
        for entry in result:
            movie = entry['Movie']
            
            # Combine Actors
            movie['actors'] = ", ".join(actor['name'] for actor in entry['Actors'])
            
            # Combine Directors
            movie['directors'] = ", ".join(director['name'] for director in entry['Directors'])
            
            # Combine Genres
            movie['genres'] = ", ".join(genre['name'] for genre in entry['Genres'])
        
        
        if result:
            return jsonify(movie),200
        else:
            return jsonify({"message": "Movie not found"}), 404
    except Exception as ex:
        return jsonify({"message": "Error occured while fetching the movie: "+fname}), 500



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080,debug=True)