# homelab-presence-reporter

A simple FastAPI application to report Proxmox server status to a Discord webhook upon receiving a POST request. This is useful for sending notifications when a user logs into a device on your network.

## How It Works

1.  A device on the network (e.g., a computer) is configured to send a POST request to the `/proxmox-status` endpoint of this application upon user login.
2.  The application receives the request, which includes the user and device name in the JSON payload.
3.  It then queries the Proxmox API to get the status of the nodes and backup server.
4.  A formatted report is generated and sent as a message to a specified Discord webhook.

## Getting Started

### Prerequisites

*   Python 3.11
*   Docker
*   A Proxmox VE environment
*   A Proxmox Backup Server (optional)
*   A Discord webhook URL

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/homelab-presence-reporter.git
    cd homelab-presence-reporter
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file in the `src` directory and add the necessary environment variables (see Configuration section).

4.  Run the application:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

## Configuration

The application requires the following environment variables to be set:

*   `PROXMOX_HOST`: The hostname or IP address of your Proxmox server.
*   `PROXMOX_USER`: The Proxmox username.
*   `PROXMOX_PASSWORD`: The Proxmox password.
*   `PROXMOX_TOKEN_NAME`: The name of the Proxmox API token.
*   `PROXMOX_TOKEN_VALUE`: The value of the Proxmox API token.
*   `PBS_HOST`: The hostname or IP address of your Proxmox Backup Server.
*   `PBS_USER`: The Proxmox Backup Server username.
*   `PBS_PASSWORD`: The Proxmox Backup Server password.
*   `PBS_TOKEN_NAME`: The name of the Proxmox Backup Server API token.
*   `PBS_TOKEN_VALUE`: The value of the Proxmox Backup Server API token.
*   `DISCORD_WEBHOOK_URL`: The URL of the Discord webhook to send notifications to.

## Usage

To trigger a report, send a POST request to the `/proxmox-status` endpoint with a JSON payload containing the `user` and `device` names:

```bash
curl -X POST http://localhost:8000/proxmox-status \
-H "Content-Type: application/json" \
-d '{"user": "test-user", "device": "test-device"}'
```

## Docker

A `Dockerfile` is provided to build a container image for the application.

*   **Build the image:**
    ```bash
    docker build -t homelab-presence-reporter .
    ```

*   **Run the container:**
    ```bash
    docker run -d -p 8000:8000 --env-file src/.env homelab-presence-reporter
    ```

## Jenkins Pipeline

The `Jenkinsfile` in this repository defines a CI/CD pipeline that automates the following stages:

1.  **Checkout**: Checks out the source code from the repository.
2.  **Build Docker Image**: Builds a new Docker image with a unique tag based on the build number.
3.  **Push to Registry**: Pushes the Docker image to a container registry and also tags it as `latest`.
4.  **Post-build Actions**:
    *   Sends a notification to a Discord channel with the build status and Docker image details.
    *   Cleans up the local Docker images created during the build.