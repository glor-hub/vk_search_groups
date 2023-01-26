# pull official base image
FROM python:3.9.9-buster

# set work directory
WORKDIR /app/vksearch

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.1.13
RUN poetry config virtualenvs.create false

COPY ../.. /app/
#COPY ./pyproject.toml /app/pyproject.toml
#COPY ./poetry.lock /app/poetry.lock

# install dependencies
RUN poetry install --no-dev --no-ansi

# copy project
#COPY . /app/
#WORKDIR /app/

EXPOSE 8000


RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
