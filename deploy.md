
# Server deployment
## Freeze requirements for deployment
Create requirements and push changes
```bash
uv pip compile pyproject.toml -o requirements.txt
```

## Setup nginx proxy
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
```bash
sudo certbot certonly --webroot -w /usr/share/nginx/letsencrypt -d glimepiride.de -d www.glimepiride.de --dry-run
```

## Setup server
On the actual server the containers are orchestrated using `docker compose`.
Login to target server, e.g., `denbi-node-5`.

```bash
# clone repository
cd /var/git
git clone https://github.com/matthiaskoenig/glimepiride-app.git
```

```bash
# redeploy the app
cd /var/git/glimepiride-app
./deploy.sh
```
