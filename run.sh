#!/bin/bash

if command -v docker >/dev/null 2>&1; then
    echo "Docker is installed"
else
    echo "Docker is not installed, please install docker first"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Docker daemon is not running, start the docker daemon first"
    exit 1
fi

# If Docker daemon is running, continue with the script
echo "Docker daemon is running. Proceeding with the script."


IMAGE_VERSION=$(cat .docker-image-version)
IMAGE_NAME="qodex-ai-frontend-agent:$IMAGE_VERSION"

# Check if the Docker image exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "Docker image '$IMAGE_NAME' does not exist. Building..."
    docker build -t $IMAGE_NAME .
    echo "Building docker image completed"
else
    echo "Docker image '$IMAGE_NAME' already exists. Skipping build."
fi

VENV_DIR="qodexai-virtual-env"

# Check if the virtual environment directory exists
if [[ -d "$VENV_DIR" ]]; then
    echo "Virtual environment '$VENV_DIR' already exists. Skipping creation."
else
    echo "Creating a Python3 virtual environment"
    python3 -m venv $VENV_DIR
    echo "Virtual environment created at '$VENV_DIR'"
fi

source $VENV_DIR/bin/activate
echo "activated a python3 virtual environment"
echo ""


echo "Installing the requirements..."
pip3 install -r requirements.txt
echo "Installed the requirements"
echo ""


if [ -f .env ]; then
  source .env
else
  echo ".env file not found!"
  exit 1
fi


CONTAINER_NAME="qodex-ai-frontend-agent"

# Check if the container exists
if docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    echo "Docker container '$CONTAINER_NAME' already exists. Stopping it..."

    # Stop the container if it is running
    docker stop "$CONTAINER_NAME"

    echo "Docker container '$CONTAINER_NAME' has been stopped."
else
    echo "Docker container '$CONTAINER_NAME' does not exist."
fi
sleep 5
echo ""

echo "Starting a new container with name as qodex-ai-frontend-agent in detached mode..."

CONTAINER_ID=$(docker run -d -it --rm \
    --env DISPLAY_NUM=1 \
    --env HEIGHT=768 \
    --env WIDTH=1024 \
    --env ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    --name qodex-ai-frontend-agent \
    $IMAGE_NAME)

echo "Docker Container ID => $CONTAINER_ID"
echo ""

# STATUS=$(docker inspect -f '{{.State.Status}}' $CONTAINER_ID)
# echo $STATUS

echo "Waiting for localhost:8080 to be available..."

# Loop until the curl command succeeds
while ! curl -s http://localhost:8080 > /dev/null; do
  echo "Service is not available. Retrying in 2 seconds..."
  sleep 2
done

echo "Service is now available on localhost:8080!"
sleep 5

echo "Started test scenarios execution..."
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY python3 execute_test_scenario.py
