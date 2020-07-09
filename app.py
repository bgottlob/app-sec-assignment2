import appsec
import os

try:
      secret_key = str.encode(os.environ['SECRET_KEY'])
except KeyError:
      print('You have not set the SECRET_KEY environment variable, so a secret key has been generated randomly')
      secret_key = os.urandom(16)

app = appsec.create_app(secret_key)
