FROM "python:3.8-alpine3.12"

MAINTAINER Brandon Gottlob "big220@nyu.edu"

# Copy local source files to app working directory
WORKDIR /usr/src/app
COPY . .

# Install pip dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove the directory the database lives in if it exists so that no data is
# burned into the Docker image
RUN rm -rf /usr/src/app/appsec/db

CMD ["python", "app.py"]
