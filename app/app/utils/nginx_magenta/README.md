# ArtFaceApp utils/nginx_magenta

This directory contains files for building supporting container with magenta neural net applying arbitrary style transfer placed on server based on uWSGI and Nginx:
- Dockerfile - dockerfile for building nginx-magenta docker image 
- requirements.txt - python dependencies to install
- entrypoint.sh - bash script for configuring Nginx (also 502 error handling)
- start.sh - bash script for supporting pre-starting commands execution, which can be added in /app/prestart.sh
- /app - default basic project for Flask in a uWSGI Nginx Docker container with Python 2.7 
- /magenta - current version of git repository of magenta tensorflow project (added into docker image)

## Building instructions:
```
$ docker build -t svponomarev/nginx-magenta .
```

Build image is placed at [DockerHub][1].

## Acknowledgements:

Basic image is taken from [tiangolo][2].
More information can be found at: [magenta/models/arbitrary_image_stylization][3]

## Authors

* **Svyatoslav Ponomarev** - sv.v.ponomarev@gmail.com

[1]: https://hub.docker.com/r/svponomarev/nginx-magenta/
[2]: https://github.com/tiangolo/uwsgi-nginx-docker
[3]: https://github.com/tensorflow/magenta/tree/master/magenta/models/arbitrary_image_stylization


