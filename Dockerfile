# =============================================================================
#  Base stage - shared setup
FROM python:3.11 as base

ARG LANGCHAIN_DEV

# System setup
ENV HOME=/root
ENV APP=/var/app
ENV PATH=$PATH:/usr/bin/ix
RUN mkdir -p /usr/bin/ix
COPY bin/* /usr/bin/ix/
RUN mkdir -p $APP
RUN mkdir -p /var/wheels

RUN apt update -y && \
    apt install -y curl postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR $APP

# Copy requirements.txt to the working directory
COPY requirements.txt .


# =============================================================================
#  PYTHON_LIB stage - Downloads and builds wheels for python libraries.
#                     This is done separately so that download cache isn't
#                     included in the final image.
FROM base as wheelhouse
RUN pip wheel -r $APP/requirements.txt -w /var/wheels


# =============================================================================
#  FRONTEND stage - Container for building the frontend with webpack and other
#                   nodejs tools.
FROM base as nodejs

# NVM / NPM Setup
ENV NVM_DIR=/usr/local/nvm
ENV NPM_DIR=$APP
ENV NODE_VERSION=18.15.0
ENV NODE_MODULES=$NPM_DIR/node_modules

RUN mkdir -p $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
ENV NODE_MODULES_BIN=$NPM_DIR/node_modules/.bin
ENV PATH $PATH:$NODE_MODULES_BIN

# build config
COPY package.json $NPM_DIR
COPY babel.config.js $NPM_DIR
COPY relay.config.js $NPM_DIR
COPY webpack.config.js $NPM_DIR

# NPM package installs
RUN echo "[$NPM_DIR]"
RUN npm install


# =============================================================================
#  APP stage produces the image:
#   - python packages
#   - compiled static
#   - nginx
FROM base as app

COPY --from=wheelhouse /var/wheels /var/wheels
RUN pip install --no-index --find-links=/var/wheels -r $APP/requirements.txt

# XXX: hacky way of generating a unique key on build, needs to be removed prior to deploy readiness
# Generate a Django secret key
# Set the Django secret key
ENV DJANGO_SECRET_KEY $(date +%s | sha256sum | base64 | head -c 32)
RUN echo "export DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}" >> /etc/profile

# FRONTEND
ENV COMPILED_STATIC=/var/static
RUN mkdir -p ${COMPILED_STATIC}

# nginx setup
RUN mkdir -p /etc/nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the rest of the application code to the working directory
COPY ix ${APP}/ix

# If LANGCHAIN_DEV is set then install the local dev version of LangChain
RUN if [ -n "${LANGCHAIN_DEV}" ]; then pip install -e /var/app/langchain/libs/langchain; fi

# Set the environment variable for selecting between ASGI and Celery
ENV APP_MODE=asgi

WORKDIR ${APP}

# Add compiled static if available.
COPY .compiled-static/ ${COMPILED_STATIC}/

# Start the application using either ASGI or Celery depending on APP_MODE
# XXX: disabling until this is tested more
#CMD if [ "$APP_MODE" = "asgi" ] export ; then python manage.py runserver 0.0.0.0:8000 ; else celery -A myapp worker -l info ; fi
