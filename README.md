# ArtFaceApp

ArtFaceApp is a [final project][1] for CS50 Harvard course "Introduction to Computer Science".

This project is a website that allows you to upload a photo of a person's face and learn about the decade of the twentieth century (1910-2000), in which this person would be in fashion, based on the similarities with the famous people of this decade. This information is used to process the uploaded photo in the style of artists and photographers of that decade.

This project allows you to learn more about the art of the twentieth century and popular people of that time, and also perhaps learn something more about yourself. From a technical point of view, the project is interesting because it uses computer vision techniques for face comparison and convolutional neural networks for image style transfer.

Working ArtFaceApp server currently can be accessed at [artfaceapp.fvds.ru][2]

Build Docker images can be found at [Docker Hub][3].

## Usage

1. Install docker

For Ubuntu 16.04:
```
$ sudo apt-get update
$ sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
$ sudo apt-get update
$ sudo apt-get install docker-ce
```

2. Install docker-compose
```
$ sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
```
3. Download docker images for this project
```
$ docker pull svponomarev/nginx-artfaceapp
$ docker pull svponomarev/tensorflow-serving-devel
$ docker pull svponomarev/nginx-magenta
```
4. Download model files

Here you can find large files that stored separately (pre-trained age & gender checkpoints converted into .pb format + colorization model):

https://drive.google.com/open?id=1SnluAuiwTjlo4tWL8hFnuUqWQGD-D6FX

Download them & extract into application directory artFaceApp/app/app

5. Launch docker containers with docker-compose
```
$ cd artFaceApp
$ docker-compose up --build
```
6. Test application in browser, default adress is http://0.0.0.0:80/

## Acknowledgements
- [ageitgey/face_recognition][4] - face detection & matching algorithm;
- [dpressel/rude-carnie][5] - age & gender prediction;
- [shunsukeaihara/colorcorrect][6] - automatic color equalization;
- [richzhang/colorization][7] - automatic image colorization;
- [acoomans/instagram-filters][8] - instagram-like image filters on Python;
- [Fred's ImageMagick Scripts: Dave Hill Effect][9];
- [vigetlabs/canvas-instagram-filters][10] - instagram-style filters in HTML5 Canvas;
- [phoboslab/WebGLImageFilter][11] - fast image filters for browsers with WebGL support;
- [tensorflow/magenta][12] - Fast Style Transfer for Arbitrary Styles;
- [MotionDesignStudio/ascii_movie_image][13] - Python ASCII Video And ASCII Image Creator;
- [mosesschwartz/warhol_effect][14] - Pop-Art Warhol Effect;
- [tiangolo/uwsgi-nginx-flask-docker][15] - examples for  uWSGI and Nginx for Flask applications in Python running in a single container;
- [How to deploy Machine Learning models with TensorFlow][16], V. Bezgachev, 2017 - mantaining tensorflow service for age and gender prediction.


## Authors

* **Svyatoslav Ponomarev** - sv.v.ponomarev@gmail.com

[1]: https://docs.cs50.net/2017/x/project.html
[2]: http://artfaceapp.fvds.ru/
[3]: https://hub.docker.com/u/svponomarev/
[4]: https://github.com/ageitgey/face_recognition
[5]: https://github.com/dpressel/rude-carnie
[6]: https://github.com/shunsukeaihara/colorcorrect
[7]: https://github.com/richzhang/colorization
[8]: https://github.com/acoomans/instagram-filters
[9]: http://www.fmwconcepts.com/imagemagick/davehilleffect/index.php
[10]: https://github.com/vigetlabs/canvas-instagram-filters
[11]: https://github.com/phoboslab/WebGLImageFilter
[12]: https://github.com/tensorflow/magenta/tree/master/magenta/models/arbitrary_image_stylization
[13]: https://gist.github.com/motiondesignstudio/9374326
[14]: https://github.com/mosesschwartz/warhol_effect
[15]: https://github.com/tiangolo/uwsgi-nginx-flask-docker
[16]: https://towardsdatascience.com/how-to-deploy-machine-learning-models-with-tensorflow-part-1-make-your-model-ready-for-serving-776a14ec3198

