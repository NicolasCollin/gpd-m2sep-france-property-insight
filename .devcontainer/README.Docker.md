# Docker README

## Building and running your docker application

When you're ready, start your application by running:

```bash
docker compose -f .devcontainer/compose.yaml run --rm -it server
```

Your application will be available at <http://localhost:8000>.

### Other useful commands (temporary)

```bash
docker compose -f .devcontainer/compose.yaml up --build --force-recreate
```

```bash
docker compose -f .devcontainer/compose.yaml run --rm -it server
```

```bash
docker compose down
```

```bash
docker ps -a
```

## Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

## References

* [Docker's Python guide](https://docs.docker.com/language/python/)
