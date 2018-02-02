# ArtFaceApp utils/tf_prediction

    This directory contains scripts for building tensorflow serving container with neural nets predicting age and gender of person by face image:
    age_prediction.py - python script for exporting age prediction model into pb format
    gender_prediction.py - python script for exporting gender prediction model into pb format
    Dockerfile.devel - fixed dockerfile for building docker image of tensorflow serving (standard dockerfile is changed to fix error: 'isnan' was not declared in this scope)

    Steps for building docker image tensorflow-serving-devel:
    1. git clone --recurse-submodules https://github.com/tensorflow/serving.git
    2. Replace Dockerfile.devel in serving/tensorflow_serving/tools/docker with its version in this repository
    3. cd serving && docker build --pull -t $USER/tensorflow-serving-devel -f tensorflow_serving/tools/docker/Dockerfile.devel .

    Build image is placed at [DockerHub][2].

    More information can be found at: V. Bezgachev, [How to deploy Machine Learning models with TensorFlow][1], 2017

## Authors

* **Svyatoslav Ponomarev** - sv.v.ponomarev@gmail.com

[1]: https://towardsdatascience.com/how-to-deploy-machine-learning-models-with-tensorflow-part-2-containerize-it-db0ad7ca35a7
[2]: https://hub.docker.com/r/svponomarev/tensorflow-serving-devel/


