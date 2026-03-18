pipeline {
    agent {
        dockerfile {
            filename 'Dockerfile'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

{%- if language == "python" %}
        stage('Setup') {
            steps {
                script {
{%- if package_manager == "uv" %}
                    sh '''
                        pip install uv
                        uv sync --all-extras
                    '''
{%- elif package_manager == "poetry" %}
                    sh '''
                        pip install poetry
                        poetry install --with dev
                    '''
{%- else %}
                    sh '''
                        python -m pip install --upgrade pip
                        pip install -e ".[dev]"
                    '''
{%- endif %}
                }
            }
        }

        stage('Lint') {
            steps {
                script {
{%- if package_manager == "uv" %}
                    sh 'uv run ruff check .'
{%- elif package_manager == "poetry" %}
                    sh 'poetry run ruff check .'
{%- else %}
                    sh 'ruff check .'
{%- endif %}
                }
            }
        }

        stage('Type Check') {
            steps {
                script {
{%- if package_manager == "uv" %}
                    sh 'uv run mypy .'
{%- elif package_manager == "poetry" %}
                    sh 'poetry run mypy .'
{%- else %}
                    sh 'mypy .'
{%- endif %}
                }
            }
        }

        stage('Test') {
            steps {
                script {
{%- if package_manager == "uv" %}
                    sh 'uv run pytest --cov=. --cov-report=xml --cov-report=html --junit-xml=junit.xml'
{%- elif package_manager == "poetry" %}
                    sh 'poetry run pytest --cov=. --cov-report=xml --cov-report=html --junit-xml=junit.xml'
{%- else %}
                    sh 'pytest --cov=. --cov-report=xml --cov-report=html --junit-xml=junit.xml'
{%- endif %}
                }
            }
        }

        stage('Security Scan') {
            steps {
                script {
{%- if package_manager == "uv" %}
                    sh 'uv run bandit -r . -ll -f json -o bandit-report.json || true'
{%- elif package_manager == "poetry" %}
                    sh 'poetry run bandit -r . -ll -f json -o bandit-report.json || true'
{%- else %}
                    sh 'bandit -r . -ll -f json -o bandit-report.json || true'
{%- endif %}
                }
            }
        }

{%- elif language == "node" %}
        stage('Setup') {
            steps {
                script {
{%- if package_manager == "pnpm" %}
                    sh '''
                        npm install -g pnpm
                        pnpm install --frozen-lockfile
                    '''
{%- elif package_manager == "yarn" %}
                    sh '''
                        npm install -g yarn
                        yarn install --frozen-lockfile
                    '''
{%- else %}
                    sh 'npm ci'
{%- endif %}
                }
            }
        }

        stage('Lint') {
            steps {
{%- if package_manager == "pnpm" %}
                    sh 'pnpm lint'
{%- elif package_manager == "yarn" %}
                    sh 'yarn lint'
{%- else %}
                    sh 'npm run lint'
{%- endif %}
            }
        }

        stage('Test') {
            steps {
{%- if package_manager == "pnpm" %}
                    sh 'pnpm test -- --coverage'
{%- elif package_manager == "yarn" %}
                    sh 'yarn test --coverage'
{%- else %}
                    sh 'npm test -- --coverage'
{%- endif %}
            }
        }

        stage('Build') {
            steps {
{%- if package_manager == "pnpm" %}
                    sh 'pnpm build'
{%- elif package_manager == "yarn" %}
                    sh 'yarn build'
{%- else %}
                    sh 'npm run build'
{%- endif %}
            }
        }

{%- elif language == "go" %}
        stage('Setup') {
            steps {
                sh '''
                    go mod download
                    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
                '''
            }
        }

        stage('Lint') {
            steps {
                sh 'golangci-lint run ./...'
            }
        }

        stage('Test') {
            steps {
                sh 'go test -v -race -coverprofile=coverage.out ./...'
            }
        }

        stage('Build') {
            steps {
                sh 'go build -o app .'
            }
        }

{%- endif %}
    }

    post {
        always {
            junit 'junit.xml' || true
            publishHTML([
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ]) || true
        }
        success {
            echo 'Build successful!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}
