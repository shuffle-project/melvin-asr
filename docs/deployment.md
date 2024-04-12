
# Deployment
## Deployment Testing
### Integration Tests

To improve our code quality, we are linting and unit-testing each Pull Request adding new code to main.
This includes a test of the unit-test coverage for our our `/src` folder of 80%.
See `.github/workflows/test.yml`.

### Smoke Tests

To make sure that new code is working, there are 2 smoke tests, one for the rest endpoint and one for the websockets endpoint.
See `/infrastrcture/smoke-test`.

**rest.py**
Call `python rest.py {port} {auth_key}` to test the REST endpoints.

**websocket.py**
Call `python websocket.py {port}` to test the Websockets endpoints.

## Deploy Process

For deploying the the ASR-API to a production/pre-production stage, there is a Docker Compose solution set up. The deployment is handled partialy by GitHub Actions, see the `.github/workflows/deploy-publish.yml` for more information. And partialy by manual steps.

Steps in Deployment:
1. **Build Docker images**: We are building a container using the Dockerfile in the root directory of the repository.

2. **Publish Docker images**: After the build process, both images are published to the GitHub packages registry of the [Shuffle-project](https://github.com/orgs/shuffle-project/).

3. **Deployment**: This step requires manual work in case you want to deploy the container standalone. It is typically deployed as a service of a compose of multiple services. 
Once the container is packed and published to the registry, the `docker-compose.yml` and the `/infrastructure` script need to copied to the Shuffle server.

4. **Starting Docker Compose**: After the deployment pipeline copied all files, the startup of the new containers is handled manually. Use Docker Compose to shut the current containers down and start the new ones. The commands are `docker compose down` and `docker compose up`. In case the Containers are not working, keep the old images to rollback the service.

5. **Smoke Tests**: As described in the section above, there are smoke tests for the REST-API and the Websocket-API of the ASR-API service. Run both against the newly running containers to make sure everything is up and running. Rollback in case there are any troubles. The REST-Endpoints `/` and `/health` can be used for an health-check as well.

6. **Config.yml**: The ASR-API is configured in the `config.yml` file. In order to spin up the docker container using docker compose, make sure the config file is availible in the `docker-compose.yml`'s directory

## Docker & Docker Compose
As ASR-API is delivered as a Docker container, there are multiple things to consider regarding Docker and Docker Compose. Currently there are deployments without a GPU and with a GPU usage in mind.

### Dockerfile
The Dockerfiles can be found at root level, there are 2 files:
1. **Dockerfile**: A simple python based container without GPU setup. This Container will not need any pre-deployment setup on the server.

1. **Dockerfile.gpu**: A more advanced container based upon a Nvidia Cuda container image, it provides support for GPUs. This Container does require a pre-deployment setup of the server.

### Docker Compose
There are 3 different compose files at root level:
1. **docker-compose.yml**: A compose file, that starts the published version of ASR-API from the GitHub container registry. Does not work with GPU.
1. **docker-compose.local.yml**: A compose file, that starts the local version of ASR-API from the local source code. It is meant for development and testing new changes. Does not work with GPU.
1. **docker-compose.gpu.local.yml**:  A compose file, that starts the local version of ASR-API from the local source code. It is meant for development and testing new changes. This one does work with a GPU. Make sure to setup your server as described in the following docs. This compose does reserve a Cuda GPU on the Host.

### Setup a Server with a CUDA GPU
To use a Docker image from Nvidia/cuda, which we are using, you are required to install the Cuda drivers and a container toolkit that connects the GPU to Docker.

1. Install the Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
2. Install the Cuda Driver for Linux Servers: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/

After everything is setup, make sure that the container you are using from Nvidia/cuda (https://hub.docker.com/r/nvidia/cuda/) does support `cudnn8` - which does require a "runtime" or "devel" type of container.

Also keep an eye on the CUDA Version. Make sure the version of your container and the version of the drivers installed on the server are matching. Mostly this means that the major verison must match, e.g. CUDA Driver 12.4 and CUDA container 12.2 will match. CUDA Driver 11.8 and CUDA container 12.0 will not match. 

