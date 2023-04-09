FROM python:3.11

ENV HOME=/root
ENV PATH=$PATH:/usr/bin/ix
RUN mkdir -p /usr/bin/ix
COPY bin/* /usr/bin/ix/
ADD .bash_profile $HOME

RUN apt update -y && apt install -y curl postgresql-client


ENV NVM_DIR=/var/app
ENV NVM_DIR=/usr/local/nvm
ENV NODE_VERSION=18.15.0
RUN mkdir -p $NVM_DIR

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default

# Set environment variables
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH


WORKDIR $NPM_DIR
COPY package.json $NPM_DIR
RUN npm install

ENV WEBPACK_OUTPUT=/var/compiled-static

# Set the working directory
RUN mkdir -p /var/app
WORKDIR /var/app


# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python requirements
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the environment variable for selecting between ASGI and Celery
ENV APP_MODE=asgi

# Expose port 8000 for ASGI, or leave it unexposed for Celery
EXPOSE 8000

# Start the application using either ASGI or Celery depending on APP_MODE
#CMD if [ "$APP_MODE" = "asgi" ] ; then python manage.py runserver 0.0.0.0:8000 ; else celery -A myapp worker -l info ; fi

# daphne <your_project_name>.asgi:application
#ENTRYPOINT = ["/usr/bin/ix/entrypoint.sh"]