FROM python:3.11

ARG LANGCHAIN_DEV

# System setup
ENV HOME=/root
ENV APP=/var/app
ENV PATH=$PATH:/usr/bin/ix
RUN mkdir -p /usr/bin/ix
COPY bin/* /usr/bin/ix/
RUN mkdir -p $APP
RUN apt update -y && apt install -y curl postgresql-client

# XXX: hacky way of generating a unique key on build, needs to be removed prior to deploy readiness
# Generate a Django secret key
# Set the Django secret key
ENV DJANGO_SECRET_KEY $(date +%s | sha256sum | base64 | head -c 32)
RUN echo "export DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}" >> /etc/profile


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

# NPM package installs
RUN echo "[$NPM_DIR]"
COPY package.json $NPM_DIR

# Static build
ENV WEBPACK_OUTPUT=/var/compiled-static
ENV COMPILED_STATIC=/var/static
RUN mkdir -p ${COMPILED_STATIC}

# nginx setup
RUN mkdir -p /etc/nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Set the working directory
WORKDIR $APP

# Llama-cpp GPU support disabled until image has required libraries
#ENV LLAMA_CUBLAS=1

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python requirements
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# If LANGCHAIN_DEV is set then install the local dev version of LangChain
RUN if [ -n "${LANGCHAIN_DEV}" ]; then pip install -e /var/app/langchain/libs/langchain; fi

# Set the environment variable for selecting between ASGI and Celery
ENV APP_MODE=asgi

WORKDIR /var/app

# Add compiled static if available.
COPY .compiled-static/* ${COMPILED_STATIC}/

# Start the application using either ASGI or Celery depending on APP_MODE
# XXX: disabling until this is tested more
#CMD if [ "$APP_MODE" = "asgi" ] export ; then python manage.py runserver 0.0.0.0:8000 ; else celery -A myapp worker -l info ; fi
