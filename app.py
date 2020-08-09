import appsec
import os

secret_dir = '/run/secrets'

# Require that password and MFA credentials are set for the admin user
def get_admin_cred(name):
      path = os.path.join(secret_dir, name)
      if os.path.isfile(path):
            with open(path, 'r') as f:
                  cred = f.read().rstrip()
            return cred
      else:
            try:
                  cred = str.encode(os.environ[name]).decode('utf-8')
                  if cred == '': raise KeyError
                  return cred
            except KeyError:
                  raise KeyError(f'You have not set the ${name} environment variable to a non-empty string')

path = os.path.join(secret_dir, 'SECRET_KEY')
if os.path.isfile(path):
      with open(path, 'r') as f:
            secret_key = f.read()
else:
      try:
            secret_key = str.encode(os.environ['SECRET_KEY'])
            # Set to empty string by default by Docker Compose
            if secret_key == b'': raise KeyError
      except KeyError:
            print('You have not set the SECRET_KEY environment variable, so a secret key has been generated randomly')
            secret_key = os.urandom(16)

app = appsec.create_app(secret_key,
                        get_admin_cred('ADMIN_PASSWORD'),
                        get_admin_cred('ADMIN_MFA'))

if __name__ == '__main__':
      app.run(host="0.0.0.0", port=5000)
