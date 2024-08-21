# Deployment

## Integration Tests

To improve our code quality, we are linting and unit-testing each Pull Request adding new code to main.
This includes a test of the unit-test coverage for our our `/src` folder of 80%.
See `.github/workflows/test.yml`.

## Deploy Process

For deploying the the project to a production/pre-production stage, there is a Docker Compose solution set up. The deployment is handled partialy by GitHub Actions, see the `.github/workflows/deploy-publish.yml` for more information. And partialy by manual steps.

Steps in Deployment:

1. **Build Docker images**: We are building a container using the Dockerfile in the root directory of the repository.

1. **Publish Docker images**: After the build process, both images are published to the GitHub packages registry of the [Shuffle-project](https://github.com/orgs/shuffle-project/).

1. **Deployment**: After the docker image has been published, use it in your compose stack to setup service in your project. Make sure to create a `config.yml` file for your needs and copy it to the root directory of the project inside the container.

## Docker & Docker Compose

As the project is delivered as a Docker container, there are multiple things to consider regarding Docker and Docker Compose. Currently there are deployments without a GPU and with a GPU usage in mind.

### Dockerfile

**Dockerfile**: An advanced container based upon a Nvidia Cuda container image, it provides support for GPUs. This Container does require a pre-deployment setup of the server, in case you want to utilize the GPU. See the following chapter `Setup a Server with a CUDA GPU`.

### Docker Compose

**docker-compose.yml**: A compose file, that starts the local version of the service from the local source code. It is meant for development and testing new changes. This one does work with a GPU. Make sure to setup your server as described in the following docs. This compose does reserve a Cuda GPU on the Host.

Check this documentation to make sure the compose setup is correct: <https://docs.docker.com/compose/gpu-support/>.

_Please make sure to use the published version of the project in case you want to run a stable version. Publishing is done via GitHub Tags._

### Setup a Server with a CUDA GPU

To use a Docker image from Nvidia/cuda, which we are using, you are required to install the Cuda drivers and a container toolkit that connects the GPU to Docker.

1. Install the Nvidia Driver on the host (e.g. for debian: <https://linuxcapable.com/how-to-install-cuda-on-debian-linux/>)
2. Install the Cuda Driver for Linux Servers: <https://docs.nvidia.com/cuda/cuda-installation-guide-linux/>
3. Install the Container Toolkit: <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>

After everything is setup, make sure that the container you are using from Nvidia/cuda (<https://hub.docker.com/r/nvidia/cuda/>) does support `cudnn` - which does require a "runtime" or "devel" type of container.

Also keep an eye on the CUDA Version. Make sure the version of your container and the version of the drivers installed on the server are matching. Mostly this means that the major version must match, e.g. CUDA Driver 12.4 and CUDA container 12.2 will match. CUDA Driver 11.8 and CUDA container 12.0 will not match.
