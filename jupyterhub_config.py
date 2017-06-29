# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

network_name = os.environ['DOCKER_NETWORK_NAME']
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
notebook_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
notebook_spawn_cmd = os.environ['DOCKER_SPAWN_CMD']

c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'

c.SwarmSpawner.jupyterhub_service_name = os.environ['JUPYTERHUB_SERVICE_NAME']
c.SwarmSpawner.networks = [network_name]
c.SwarmSpawner.notebook_dir = notebook_dir
mounts = [
    {
        'type' : 'volume',
        'source' : 'jupyter-{username}',
        'target' : notebook_dir
    },
    {                                                      
    'type' : 'bind',
    'source' : '/data/cablab',
    'target' : '/home/jovyan/work/datacube'
    }
]
c.SwarmSpawner.container_spec = {
    # The command to run inside the service
    'args' : [notebook_spawn_cmd],
    'Image' : notebook_image,
    'mounts' : mounts
}
c.SwarmSpawner.start_timeout = 60 * 1
c.SwarmSpawner.service_prefix = os.environ['JUPYTER_NB_PREFIX']

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = '0.0.0.0'

# TLS config
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')
c.JupyterHub.db_url = os.path.join('sqlite:///', data_dir, 'jupyterhub.sqlite')
c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)
