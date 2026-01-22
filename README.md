# student-election

## Deployment

This repository contains a Flask application that uses Firebase Admin for authentication. Below are quick deployment options.

- Docker (recommended):

	Build image:

	```bash
	docker build -t student-election:latest .
	```

	Run container (binds to port 5000):

	```bash
	docker run -p 5000:5000 --env FLASK_ENV=production student-election:latest
	```

- Heroku (quick):

	```bash
	heroku create
	git push heroku main
	heroku ps:scale web=1
	```

	Make sure `firebase_credentials.json` is provided as a config var or stored securely; do NOT commit credentials to the repo.

Notes:
- Ensure `firebase_credentials.json` is present on the server or provided securely as an environment secret.
- By default the app uses port `5000` and the `SECRET_KEY` in `app.py` — change this secret key for production.

## Continuous Deployment (GitHub Actions)

A GitHub Actions workflow is provided to build and publish a Docker image to GitHub Container Registry (GHCR) on pushes to `main` or `master`.

- The workflow file is `.github/workflows/docker-publish.yml` and uses the repository's `GITHUB_TOKEN` to push the image.
- Published image tags:
	- `ghcr.io/<OWNER>/student-election:latest`
	- `ghcr.io/<OWNER>/student-election:<COMMIT_SHA>`

If you prefer Docker Hub, create `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets and modify the workflow to log in to `docker.io`.

