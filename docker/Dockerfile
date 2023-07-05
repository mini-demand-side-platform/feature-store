# `python-base` sets up all our shared environment variables
FROM python:3.9.6-slim as python-base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.3.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 

# `builder-base` stage is used to build deps + create our virtual environment
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python - --version $POETRY_VERSION
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
# copy project requirement files here to ensure they will be cached.
WORKDIR /usr/src/app
COPY poetry.lock pyproject.toml ./
COPY feature_store ./feature_store

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi
CMD ["uvicorn", "feature_store.main:app", "--host", "0.0.0.0", "--port", "8000"]