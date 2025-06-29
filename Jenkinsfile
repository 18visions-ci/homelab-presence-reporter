pipeline {
    agent any

    environment {
        REGISTRY_URL        = 'registry-prod.iworksometimes.com'
        IMAGE_NAME          = 'homelab-presence-reporter'
        IMAGE_TAG           = "${env.BUILD_NUMBER}"
        DISCORD_WEBHOOK_URL = credentials('jenkins_build_discord_webhook')  // store your webhook URL as a Secret Text credential
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG} .
                '''
            }
        }

        stage('Push to Registry') {
            steps {
                sh '''
                    echo "Pushing Docker image..."
                    docker push ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}

                    echo "Tagging as latest..."
                    docker tag ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY_URL}/${IMAGE_NAME}:latest

                    echo "Pushing latest tag..."
                    docker push ${REGISTRY_URL}/${IMAGE_NAME}:latest
                '''
            }
        }
    }

    post {
        always {
            script {
                // Capture build result
                def status  = currentBuild.currentResult
                def job     = env.JOB_NAME
                def number  = env.BUILD_NUMBER
                def branch  = env.BRANCH_NAME ?: 'N/A'
                def url     = env.BUILD_URL

                // Compose a code-block message
                def message = "🔔 Jenkins Build Notification for **${job}**\n" +
                            "Build URL: ${url}\n\n" +
                            "```\n" +
                            "Build Number : #${number}\n" +
                            "Branch       : ${branch}\n" +
                            "Status       : ${status}\n" +
                            "Docker Image : ${REGISTRY_URL}/${IMAGE_NAME}:${number}\n" +
                            "Latest Tag   : ${REGISTRY_URL}/${IMAGE_NAME}:latest\n" +
                            "```"

                // Convert to valid JSON
                def payload = groovy.json.JsonOutput.toJson([ content: message ])

                // Send to Discord
                sh """
                  curl -s -X POST "$DISCORD_WEBHOOK_URL" \\
                    -H 'Content-Type: application/json' \\
                    -d '${payload}'
                """
            }

            // Clean up local images
            sh '''
                docker rmi ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG} || true
                docker rmi ${REGISTRY_URL}/${IMAGE_NAME}:latest         || true
            '''
            cleanWs()
        }
    }
}