# Glimepiride webapp
This repository contains the code of the digital twin of glimepiride.
The model repository is available from [https://github.com/matthiaskoenig/glimepiride-model.git](https://github.com/matthiaskoenig/glimepiride-model.git).

# Local Development
### Installation
Use `uv` to setup the dependencies
```
uv venv
uv sync
```

### Run app
To run the app locally use
```bash
cd src
marimo run app.py 
```

### Edit app
To modify the app use
```bash
cd src
marimo edit app.py
```


# Deployment
## Freeze requirements for deployment
Create requirements
```bash
uv pip compile pyproject.toml -o requirements.txt
```

## Setup proxy
- login to proxy server `denbi-head`

**Activate page**  
The page must be copied and activated. Make sure to **update the IP** of the server in nginx configuration!
```
cp <repo>/nginx/glimepiride.de /etc/nginx/sites-available/glimepiride.de
sudo ln -s /etc/nginx/sites-available/glimepiride.de /etc/nginx/sites-enabled/
```

### Certificates
#### Initial certificates
```
sudo mkdir -p /usr/share/nginx/letsencrypt
sudo service nginx stop
sudo certbot certonly

-> glimepiride.de www.glimepiride.de

sudo service nginx start
sudo service nginx status
```

#### Certificate renewal
```
sudo certbot certonly --webroot -w /usr/share/nginx/letsencrypt -d glimepiride.de -d www.glimepiride.de --dry-run
```

## Setup server
On the actual server the containers are orchestrated using `docker-compose`.
Login to server `denbi-node-5`.

### Initial setup
```
cd /var/git
git clone https://github.com/matthiaskoenig/glimepiride-app.git
```

**start containers**
Pull latest changes 
```
./deploy.sh
```
