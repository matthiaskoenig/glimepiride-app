# Glimepiride Web Application "Digital Twin"
This repository contains the code of the digital twin of glimepiride.
The model repository is available from [https://github.com/matthiaskoenig/glimepiride-model.git](https://github.com/matthiaskoenig/glimepiride-model.git).

## Run with docker
```bash
# Build your image, and tag it as my_app
docker build -t glimepiride_app .

# Start your container, mapping port 8080
docker run -p 4567:8080 -it glimepiride_app
```
The app is then available from http://localhost:4567


## Run locally
Use `uv` to setup the dependencies
```bash
uv venv
uv sync
```

To run the app locally use
```bash
marimo run src/app.py 
```

To modify the app use
```bash
cd src
marimo edit app.py
```
