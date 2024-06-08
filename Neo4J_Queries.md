# Neo4J Queries

### Steps to import the csv file to neo4J dbms
* Copy the IMDB-Movie-Data.csv file
* Navigate to the neo4j Database path:
    *  Sample path: </br>
    `C:\Users\<USERNAME>\.Neo4jDesktop\relate-data\dbmss\<DBMS_UNIQUE_ID>\import`
* Paste the file into the import directory.

## 1. Add all the movies from the CSV file to the Neo4j database | Cipher Query

* <em>Insert Movie data with revenue:</em></br>
<pre>
LOAD CSV WITH HEADERS FROM "file:///IMDB-Movie-Data.csv" AS row
WITH row.Ids AS i, row.Title AS t, row.Description AS d, row.Year AS y, row.Runtime AS r, row.Rating AS rt, row.Votes AS v, row.Revenue AS rv
WHERE rv IS NOT NULL
MERGE (:Movie{ids:i, title:t, description:d, year:y, runtime:r, rating:rt, votes: v, revenue:rv})
</pre>

*  <em>Insert Movie date without revenue:</em> </br>
<pre>
LOAD CSV WITH HEADERS FROM "file:///IMDB-Movie-Data.csv" AS row
WITH row.Ids AS i, row.Title AS t, row.Description AS d, row.Year AS y, row.Runtime AS r, row.Rating AS rt, row.Votes AS v, row.Revenue AS rv
WHERE rv IS NULL
MERGE (m:Movie{ids:i, title:t, description:d, year:y, runtime:r, rating:rt, votes: v})
ON CREATE SET m.revenue = NULL
</pre>

* <em>Create Nodes : [Person, Genre] and make relations with movies as [ACTED_IN], [DIRECTED], [IN] </em></br>
<pre>
LOAD CSV WITH HEADERS FROM "file:///IMDB-Movie-Data.csv" AS row
WITH row.Ids AS t, SPLIT(row.Actors,',') AS a, SPLIT (row.Genre, ',') AS g, row.Director AS d
UNWIND t AS t1
UNWIND a AS a1
UNWIND g AS g1
UNWIND d AS d1
WITH *, trim(a1) AS actor, trim(g1) AS genre , trim(d1) AS director  
MERGE (:Person{name:actor})
MERGE (:Person{name:director})
MERGE (:Genre{name:genre})
WITH *,actor,genre,director
MATCH (mo:Movie{ids:t1}),(ac:Person{name:actor}),(gn:Genre{name:genre}),(di:Person{name:director})
MERGE (ac)-[:ACTED_IN]->(mo)
MERGE (di)-[:DIRECTED]->(mo)
MERGE (mo)-[:IN]->(gn)
RETURN mo, ac, gn, di
</pre>

## 2. Delete all the movies from the Neo4j database | Cipher Query

<pre>
MATCH (n) DETACH DELETE n
</pre>




## 3. Insert the new movie information | Cipher Query 
<pre>
CREATE (m:Movie {
    title: "The Watchers",
    description: "When 28-year-old artist Mina finds shelter after getting stranded in an expansive, untouched forest in western Ireland, she unknowingly becomes trapped alongside three strangers that are watched and stalked by mysterious creatures each night.",
    ids: "1001",
    rating: "5.4",
    revenue: "100.69",
    runtime: "102",
    votes: "38552",
    year: "2024"
}) 

WITH m
UNWIND [
    {name: "Dakota Fanning"},
    {name: "Georgina Campbell"},
    {name: "Alistair Brammer"},
    {name: "Hannah Howland"}
] AS actor
MERGE (a:Person {name: actor.name})
MERGE (a)-[:ACTED_IN]->(m)

WITH m
UNWIND [
    {name: "Ishana Night Shyamalan"}
] AS director
MERGE (d:Person {name: director.name})
MERGE (d)-[:DIRECTED]->(m)

WITH m
UNWIND [
    {name: "Horror"},
    {name: "Mystery"},
    {name: "Thriller"}
] AS genre
MERGE (g:Genre {name: genre.name})
MERGE (m)-[:IN]->(g)
</pre>

### 4.	Update the movie information using title. (By update only title, description, and rating) | Cipher Query
<pre>
MATCH (m:Movie{title:'The Watchers'}) SET m.title = 'The Watchers 2024' , m.description = 'Sample Description' , m.rating = '6.5'
</pre>

### 5. Delete the movie information using title | Cipher Query
<pre>
MATCH (m:Movie{title:'Trolls'}) DETACH DELETE m 
</pre>

### 6. Retrieve all the movies in database. | Cipher Query
<pre>
MATCH (m:Movie) RETURN m as Movie
</pre>

### 7. Display the movie’s details includes actors, directors and genres using title | Cipher Query
<pre>
MATCH (m:Movie{title:'The Watchers'})
    OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
    OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
    OPTIONAL MATCH (m)-[:IN]->(g:Genre)
    RETURN m AS Movie, COLLECT(DISTINCT a) AS Actors, COLLECT(DISTINCT d) AS Directors, COLLECT(DISTINCT g) AS Genres;
</pre>