FROM python:3.8.5
WORKDIR /code
COPY requirements.txt /code
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /code
CMD python manage.py collectstatic
CMD gunicorn foodgram_project.wsgi:application --bind 0.0.0.0:8000