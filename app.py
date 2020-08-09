import appsec
import os

# Require that password and MFA credentials are set for the admin user
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

try:
      secret_key = str.encode(os.environ['SECRET_KEY'])
      # Set to empty string by default by Docker Compose
      if secret_key == b'': raise KeyError
except KeyError:
      print('You have not set the SECRET_KEY environment variable, so a secret key has been generated randomly')
      secret_key = os.urandom(16)

app = appsec.create_app(secret_key, admin_password, admin_mfa)

if __name__ == '__main__':
      app.run(host="0.0.0.0", port=5000)
