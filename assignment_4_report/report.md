---
documentclass: extarticle
author: Brandon Gottlob
fontsize: 13pt
linestretch: 2 
geometry: margin=0.75in
indent: true
header-includes: |
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{ifsym}
    \usepackage{fancyhdr}
    \pagestyle{fancy}
    \fancyhead[LO,LE]{Brandon Gottlob}
    \fancyhead[RO,RE]{Assignment 4 Report}
    \fancyfoot[LO,LE]{\today}
pagestyle: empty
lang: en-US
---

# Assignment 4

## Repository Link

[https://github.com/bgottlob/app-sec-assignment2](https://github.com/bgottlob/app-sec-assignment2)

\noindent
This is the same repository used for assignments 2 and 3.
Additional commits have been added to implement assignment 4.
The following link is to a tag for the code submitted as assignment 4:

[https://github.com/bgottlob/app-sec-assignment2/releases/tag/v3.0](https://github.com/bgottlob/app-sec-assignment2/releases/tag/v3.0)

## Docker Compose Usage

In order to run the application using docker-compose, run the following command:
```
ADMIN_PASSWORD=<admin_password> ADMIN_MFA=<admin_mfa_number> [SECRET_KEY=<secret_key>] \
  [PORT=<port>] docker-compose [-d]
```

`ADMIN_PASSWORD` and `ADMIN_MFA` are required variables.
`SECRET_KEY` is an optional variable, since the Flask server will automatically generate a random secret key on startup when it is not provided.

`PORT` is the port Docker exposes to run the web server on.
This is set to `8080` by default in the `.env` file.
Internally to the container, the exposed PORT will be mapped to port 5000.
This causes Flask to log that the server is running on port 5000, even if it is exposed to a different external port number.

Alternatively, the environment variables can be set prior to running `docker-compose`:
```
export ADMIN_PASSWORD=<admin_password>
export ADMIN_MFA=<admin_mfa_number>
export SECRET_KEY=<secret_key>
export PORT=<port>
```

Since the `docker-compose.yml` file contains the setting `build: .`, running the `docker-compose` command will automatically trigger the image to be built.

### Dockerfile Configuration

The specific base image chosen to build the Docker image for this application is `python:3.8-slim-buster`.
This is a Docker [Official Image](https://docs.docker.com/docker-hub/official_images/) that has Python 3.8 and pip pre-installed on Ubuntu Buster.
A Docker Official Image was chosen because they are verified to be following Docker best practices and receive frequent security updates because official images are popular among the Python community.
The risk of malicious code slipping into an official Python base image without anyone in the community first noticing is low.
For Python, I have pinned the major and minor version number, but not the patch version.
This protects my application from any breaking changes that could come with a minor or major version update while still picking up new patch versions for bug fixes and security patches.
This is a reasonable balance between lowering the frequency of unexpected changes while keeping up to date for security purposes.
The "slim" variant of Ubuntu Buster is chosen since the image size is smaller and more optimized for container usage than is the standard Ubuntu Buster base image.

The Dockerfile is relatively simple.
It copies the local source code tree to a pre-defined app working directory on the image.
Next, the `requirements.txt` file is used to install pip packages on the image.
Finally, the `appsec/db` directory is removed if present in the source tree, as this directory contains the SQLite database file.
Removing this directory prevents a local database from being burned into the image.

### Docker Compose Configuration

The `docker-compose.yml` is also relatively simple.
It creates one service called `web`, which represents the application.
It instructs that the image used should be the result of building Dockerfile located in the current directory.
The container's internal port of 5000, where Flask runs, is exposed as a different port specified by the PORT shell environment variable.
As previously mentioned, the default of 8080 is specified by the `.env` file.
Lastly, the shell environment variables `SECRET_KEY`, `ADMIN_PASSWORD`, and `ADMIN_MFA` are passed through from the shell to the running container.

### Application Code Changes

In order to run the application cleanly in the dockerized environment, some changes needed to be made.
First, the following lines were added to `app.py`:

``` python
if __name__ == '__main__':
      app.run(host="0.0.0.0", port=5000)
```

Simply put, this allows for the Flask server to expose itself on any IP address on port 5000 when run using the command `python app.py`.
This is the startup command specified by the `Dockerfile`.
The `if` condition allows for the server to still run on localhost when run using `flask run`.

The following code was added to require that an admin password and MFA number are provided as environment variables:

``` python
try:
      admin_password = str.encode(os.environ['ADMIN_PASSWORD']).decode('utf-8')
      if admin_password == '': raise KeyError
except KeyError:
      raise KeyError('You have not set the ADMIN_PASSWORD environment variable to a non-empty string')

try:
      admin_mfa = str.encode(os.environ['ADMIN_MFA']).decode('utf-8')
      if admin_mfa == '': raise KeyError
except KeyError:
      raise KeyError('You have not set the ADMIN_MFA environment variable to a non-empty string')
```

The `docker-compose` command will set any environment variables that are not set at the shell level to empty strings, so an additional empty string check is made before proceeding to start the application.
From here, the admin_password and admin_mfa variables are passed down to the `create_app()` function then to the `create_admin_account()` functions.
An additional check for an empty bytes set was made for the secret key to account for `docker-compose` default behavior:

``` python
if secret_key == b'': raise KeyError
```

## Docker Content Trust

Docker Content Trust allows for images to be signed and for local docker clients to verify the signatures of pulled images.
This is critical in ensuring that images deployed to production hosts are not tampered with in any way before they are executed by containers.

In a production deployment infrastructure would contain three classes of hosts: continuous deployment (CD) hosts, application hosts, and Docker registry hosts.
The CD hosts would build and sign Docker images and push them to a Docker registry host, which verifies the signatures.
The application hosts would then pull down signed Docker images from the registry, then instantiate containers to run application code.

On a network level, CD hosts should have no way of directly contacting application hosts.
Additionally, CD hosts should only be accessible by the privileged maintainers of an application and should not be accessible by any external users.
In the case of a large organization, CD hosts would belong in the organization's internal network.
In order to service end users, application hosts will be acessible on the public Internet.
Depending on whether the images are for a proprietary or open source application, the registry hosts may be private or public, like in the case of Docker Hub.
In the case of a private registry, the registry hosts should be in an internal company network and only accessible by application hosts.
These constraints can take the form of a firewall with application hosts explicitly whitelisted.

A root key must first be created for a given image tag in order to sign it.
On a CD host, Docker Content Trust would be enabled by setting the `DOCKER_CONTENT_TRUST` environment variable to `1` then performing some action with the registry, such as a `docker push`.
This triggers creation of a root key, which is the root of trust for the image tag, and a targets key, which is used to sign images.
These two keys are created and stored on the CD host locally.
On the Docker registry, the internal Notary server generates timestamp and snapshot keys, which prevent certain classes of attacks on the registry itself.
In addition to generating a strong passphrase for the root key, it should be backed up then taken offline and out of the `~/.docker/trust/private` directory of the CD host, such as on encrypted USB keys.
From here, the private targets key used to sign images can be securely transferred to each CD host.
Targets keys should be regenerated periodically, which will require usage of the root key to establish trust in newly generated targets keys.
All application hosts will be provisioned with the `DOCKER_CONTENT_TRUST` environment variable set to `1`.
This allows only signed images verified by the Docker registry to be used for running containers.

## Docker Swarm

### Usage

To use Docker Swarm, first initialize a Docker Swarm on your host with the command `docker swarm init`.
This switches your host to running in swarm mode with the current host as the swarm manager.
Additional hosts can join the swarm using `docker swarm join`.
However, this assignment considers swarm deployment only on one node, though it is transferrable to multi-node setups.
Next, set up Docker secrets for `SECRET_KEY`, `ADMIN_PASSWORD`, and `ADMIN_MFA` using the following commands:

```
echo "<secret_key>" | docker secret create SECRET_KEY -
echo "<admin_password>" | docker secret create ADMIN_PASSWORD -
echo "<admin_mfa_number>" | docker secret create ADMIN_MFA -
```

The image for the web application must first be built.
If it has not been built already by running `docker-compose`, manually trigger it to be built using the command `docker-compose build`.
Finally, deploy the web application in swarm mode using the following command:

```
docker stack deploy -c docker-swarm.yml appsec
```

The logs of the four web application replicas can be accessed using `docker service logs [-f] appsec_web`.
The optional `-f` flag tails the logs.

The web application can now be accessed by navigating to port 8080 on your host in a browser.
When tailing the logs, it can be observed that requests are load balanced to the four replicas by checking the container name prefixed to each log.
The four replicas share a Docker volume and thus share the same database, so the user should not notice that four different containers are servicing requests.

To destroy the docker swarm, run `docker stack rm appsec`.
Additionally, remove the Docker volume used for the database with `docker volume rm appsec_db_sqlite`.
If the docker volume is not removed, the next time the application is deployed, the database will persist and will not be cleared for the new Docker stack.
Secrets can be removed using `docker secret rm <secret_name>`.

### Configuration

In order to deploy the web application using Docker Swarm, some additional changes were made to the application and to the Docker Compose file.
Specifically, a new Docker Compose file named `docker-swarm.yml` is used to deploying to Docker Swarm.
The original `docker-compose.yml` file is still used for running the application locally with Docker Compose.

The most notable difference in the Docker Swarm configuration is the handling of secrets using Docker secrets.
Docker secrets are a more secure way to store secrets, since they are stored in encrypted files instead of plaintext environment variables.
Environment variables are acceptable for running locally for development, but not in production.
Addtionally, Docker secrets are synchronized across the nodes of a swarm using the Raft distributed consensus algorithm.
The three environment variables `SECRET_KEY`, `ADMIN_PASSWORD`, and `ADMIN_MFA` are now passed to the application containers as files in the `/run/secrets` directory.
The following code snippet is an excerpt of the code changes required to account for this:

``` python
path = os.path.join(secret_dir, name)
if os.path.isfile(path):
    with open(path, 'r') as f:
          cred = f.read().rstrip()
    return cred
```

This code runs before the environment variables are checked, so that secret files will be used before shell environment variables are considered.
Additionally, the following configuration in `docker-swarm.yml` forces that environment variables are empty strings, which forces Docker secrets as the only way to pass in secrets in Docker Swarm:

``` yaml
environment:
  SECRET_KEY: ''
  ADMIN_PASSWORD: ''
  ADMIN_MFA: ''
```

Four containers run the web application in parallel, as specified by the `replicas` configuration attribute.
The following configuration instructs Docker Swarm to reserve at least 25% of CPU and 50 MB of memory on the host machine to the containers running the web application and limiting them to 50% CPU and 100 MB of memory:

``` yaml
resources:
  limits:
    cpus: '0.50'
    memory: 100M
  reservations:
    cpus: '0.25'
    memory: 50M
```

In order to share the same database, a Docker volume is created to point to the `appsec/db` directory, where the SQLite database file is stored.
This allows all four replicas to share the same database file.
Due to SQLite's simplicity in its full database locking scheme, this does not provide performance benefits, but does give redundancy at the application level if any of the replicas crash.

``` yaml
volumes:
  - db_sqlite:/usr/src/app/appsec/db
```
