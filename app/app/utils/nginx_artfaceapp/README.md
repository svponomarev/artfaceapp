# ArtFaceApp utils/nginx_artfaceapp

This directory contains files for building main artfaceapp container with development server based on uWSGI and Nginx:

- Dockerfile - dockerfile for building nginx-artfaceapp docker image;
- requirements.txt - python dependencies to install;
- entrypoint.sh - bash script for configuring Nginx (also 502 error handling);
- start.sh - bash script for supporting pre-starting commands execution, which can be added in /app/prestart.sh;
- /app - default basic project for Flask in a uWSGI Nginx Docker container with Python 2.7; 

## Building instructions:
```
$ docker build -t svponomarev/nginx-artfaceapp .
```

Build image is placed at [DockerHub][1].

## Acknowledgements:

Basic image is taken from [tiangolo][2].
More information can be found at: [https://ianlondon.github.io/blog/deploy-flask-docker-nginx/][3]

## Authors

* **Svyatoslav Ponomarev** - sv.v.ponomarev@gmail.com

[1]: https://hub.docker.com/r/svponomarev/nginx-artfaceapp/
[2]: https://github.com/tiangolo/uwsgi-nginx-docker
[3]: https://ianlondon.github.io/blog/deploy-flask-docker-nginx/
