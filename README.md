# Yamdb API
## Provides an API for the YaMDb service, a database of reviews of movies, books, and music.
### User role:
<li>Anonymous — can view descriptions of works, read reviews and comments.
<li>Authenticated user (user) — can read everything, as well as Anonymous, can additionally publish reviews and rate works (movies/books/songs), can comment on other people's reviews and give them ratings; can edit and delete their reviews and comments.
<li>Moderator (moderator) — the same rights as an Authenticated user, plus the right to delete and edit any reviews and comments.
<li>Administrator (admin) — full rights to manage the project and all its contents. Can create and delete works, categories, and genres. Can assign roles to users.
<li>Django administrator — the same rights as the Administrator role.</li>

### User registration algorithm:
<li>The user sends a POST request with the email parameter to / api/v1/auth/email/.
<li>YaMDB sends an email with a confirmation code (confirmation_code) to the email address.
<li>The user sends a POST request with the email and confirmation_code parameters to /api/v1/auth/token/, and receives a token (JWT token) in response to the request.</li>

The project is based on the Django Framework. To run it on a local machine, use the command: python manage.py runserver.
Detailed API documentation is available at the local address 127.0.0.1/redoc.
