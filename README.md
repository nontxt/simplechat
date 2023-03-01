# simplechat
This is a simple chat application on django, with DRF and simple-jwt authentication.

## Steps to run the application:
1. Clone this repository
2. Go ahead in the project directory
   * If you have pipenv, in your command line:
     1. Run `pipenv shell`
     2. Run `pipenv install` 
   * If you use virtualenv:
     1. Activate the virtualenv
     2. Run `pip install -r requirements.txt` in your command line
3. Go ahead in the `simplechat` directory
4. Run `python manage.py makemigrations`
5. Run `python manage.py migrate`
6. Run `python manage.py test` for run unittests
7. Run `python manage.py createsuperuser` and fill superuser credentials
8. Run `python manage.py runserver`


## Edpoints:
### Auth:
| Endpoint             | Method | Parameters             | Description                          |
|----------------------|--------|------------------------|--------------------------------------|
| `token/`             | POST   | _username_, _password_ | Obtain simple bearer token from DRF  |
| `token/jwt/`         | POST   | _username_, _password_ | Obtain jwt access and refresh tokens |
| `token/jwt/refresh/` | POST   | _refresh_              | Obtain new jwt access token          |
| `admin/`             | GET    |                        | Admin site                           |

### API:

| Endpoint                           | Method | Parameters                                   | Description                                                              |
|------------------------------------|--------|----------------------------------------------|--------------------------------------------------------------------------|
| `api/threads`                      | GET    |                                              | Return current user threads                                              |
| `api/threads/{username}`           | GET    | _username_                                   | Create and return new thread with user or return thread if it does exist |
| `api/threads/{username}`           | DELETE | _username_                                   | Delete existing thread                                                   |
| `api/messages/{username}`          | GET    | _username_                                   | Return messages from thread with user                                    |
| `api/messages/{username}`          | POST   | _username_, _text_                           | Sent messages to user in this thread                                     |
| `api/messages/unread`              | GET    |                                              | Return unread messages for current user                                  |
| `api/messages/unread/mark_as_read` | POST   | _message_id_ - must be single or list of ids | Mark provided messages as read                                           |

**Note**: For using this API you must provide token for authenticate