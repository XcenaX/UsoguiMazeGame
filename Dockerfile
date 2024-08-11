FROM python:3.8

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

RUN python manage.py migrate

CMD ["daphne", "-b", "0.0.0.0", "-p", "8080", "maze.asgi:application"]