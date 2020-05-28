# Project 1

Web Programming with Python and JavaScript
SITE ORGANISATION FOR PROJECT1
The website is named REEDA: A book review website
1.	The first page of the website is the home page which stands as the cover page of the website. The page contains some useful links to access the website like the signup and login links as well as a brief description of the website.
2.	Once a user signs up to the website, he is redirected to the login page where he can login with his created credentials
3.	When the user logs in, he is taken to the books page; the books page is where all the books are displayed and the books are displayed according to their ISBN, Title, Author, Year of publication as well as giving users an opportunity to write a review about any of the books.
For quick access to a book, a search can be carried out and the search query can be anything ranging from book ISBN, title, author or publication year.
Once search results are displayed, the user can click on any of the books to see the full details of the book as well as write a review about the book. 
When done, the user can logout of the website.
4.	Users can make a GET request to the website’s API using a book’s ISBN. A JSON response is returned containing book title, author, publication date, ISBN, review count, average score.  
5. The main application file is the application.py while the books.csv contains the details about the different books in a comma seperated values style. Import.py commits the details of the books.csv file to the database.
