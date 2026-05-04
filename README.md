SwiftDeploy: Canary Deployment Engine SwiftDeploy is a custom CLI tool designed to automate the deployment of a resilient, canary-aware API stack. It dynamically generates infrastructure configurations based on a manifest.yaml file, manages a dual-service architecture (FastAPI & Nginx), and ensures the stack is healthy before finalizing deployment.

Features

Dynamic Configuration: Generates docker-compose.yml and nginx.conf at runtime in the project root.

Canary Logic: Implements a middleware-based "chaos" and header system for canary testing.

Resilient Healthchecks: Orchestrates service startup using Docker healthchecks to ensure Nginx only starts once the API is fully ready.

Custom Observability: Nginx is configured with a pipe-delimited log format for easier parsing and monitoring.

Security Focused: Runs services as a non-root user (swiftuser) and drops unnecessary Linux capabilities.

Prerequisites

Docker Desktop (with Compose support)

Python 3.11+

Curl (for healthcheck verification)

1: create main.py and requirement.txt ( main.py track MODE, starttime and chaos config, requirements; fastapi,uvicorn,pydantic)

local testing to ensure logic works;

pip install -r app/requirements.txt

curl.exe -i http://localhost:5050

2: multistage docker:

to build the image :

docker build -t keed-swift-node:v1 .

3: since swiftdeploy need to generate configurations programmatically, i dont write the final docker-compose.yml or nginx.conf by hand. i created jinja2 templates that acts as blueprints. This templates needs to handle the custom logging, the Json erroe bodies and the header farwarding requirements.

Docker compose template : This defines the relationship between the API and nginx.

Manifest.yaml ( the source of the truth) This is the only file allowed to be edited manually.

network: driver_type: bridge name: keed-net-stage4

nginx: image: nginx:latest port: 7070
proxy_timeout: 60

services: image: keed-swift-node:v1
mode: canary port: 5050

4: Build the swiftdeploy cli using python.

first ensure the necessary librarier are installed on the host machine to run the CLI.

pip install pyyaml jinja2

create a file name swiftdeply, make is executable.

Validate :

python swiftdeploy validate ( this checks if your image and manifest are ready)

Generates files:

python swiftdeploy init . (nginx.conf and docker-compose.yml should appear magically)

Start everything:

python swiftdeploy deploy ( this brings the containers up and waits for the API to say "stack is healthy"

Verify the nginx gateway test that the nginx is actually routing traffic and adding the required headers.

curl.exe -i http://localhost:7070/
