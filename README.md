# Glimepiride webapp

## Installation
```
uv venv
uv sync
```

## Edit app
```bash
cd src
marimo edit app.py
```

## Run app
```bash
cd src
marimo run app.py 
```

## Deployment
Create requirements
```bash
uv pip compile pyproject.toml -o requirements.txt
```
Test locally
# Build your image, and tag it as my_app
```bash
docker build -t glimeperide_app .
```
# Start your container, mapping port 8080
docker run -p 4567:8080 -it glimeperide_app

# Visit http://localhost:4567