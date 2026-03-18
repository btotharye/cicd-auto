"""Data models for project analysis."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProjectAnalysis:
    """Complete project analysis result."""

    # Core detection
    language: str  # "python", "node", "go", "rust", etc.
    framework: Optional[str] = None  # "fastapi", "django", "express", etc.
    package_manager: Optional[str] = None  # "uv", "poetry", "npm", "cargo", etc.
    test_framework: Optional[str] = None  # "pytest", "jest", "go test", etc.
    
    # Platform detection
    platform: Optional[str] = None  # "github", "gitlab", "jenkins", "buildkite", etc.
    cloud: Optional[str] = None  # "aws", "gcp", "azure", "docker", etc.
    
    # Build/deploy info
    has_dockerfile: bool = False
    has_terraform: bool = False
    has_k8s: bool = False
    
    # Inferred commands
    test_command: Optional[str] = None  # e.g., "pytest", "npm test", "go test ./..."
    lint_command: Optional[str] = None  # e.g., "ruff check .", "eslint ."
    build_command: Optional[str] = None  # e.g., "uv build", "npm run build"
    
    # Python-specific
    python_version: Optional[str] = None  # "3.11", "3.12", etc.
    
    # Metadata
    files_found: dict = field(default_factory=dict)  # Important files and their paths


class Language:
    """Supported programming languages."""
    
    PYTHON = "python"
    NODE = "node"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CSHARP = "csharp"
    RUBY = "ruby"
    PHP = "php"
    
    ALL = [PYTHON, NODE, GO, RUST, JAVA, CSHARP, RUBY, PHP]


class PackageManager:
    """Supported package managers."""
    
    # Python
    UV = "uv"
    POETRY = "poetry"
    PIPENV = "pipenv"
    PIP = "pip"
    
    # Node
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    BUN = "bun"
    
    # Go
    MOD = "go mod"
    GOPATH = "gopath"
    
    # Rust
    CARGO = "cargo"
    
    # Java
    MAVEN = "maven"
    GRADLE = "gradle"
    
    # Ruby
    BUNDLER = "bundler"
    
    ALL = [UV, POETRY, PIPENV, PIP, NPM, YARN, PNPM, BUN, MOD, GOPATH, CARGO, MAVEN, GRADLE, BUNDLER]


class TestFramework:
    """Supported test frameworks."""
    
    # Python
    PYTEST = "pytest"
    UNITTEST = "unittest"
    NOSE2 = "nose2"
    
    # Node
    JEST = "jest"
    MOCHA = "mocha"
    VITEST = "vitest"
    
    # Go
    GO_TEST = "go test"
    
    # Rust
    CARGO_TEST = "cargo test"
    
    ALL = [PYTEST, UNITTEST, NOSE2, JEST, MOCHA, VITEST, GO_TEST, CARGO_TEST]


class Platform:
    """Supported CI/CD platforms."""
    
    GITHUB = "github"
    GITLAB = "gitlab"
    JENKINS = "jenkins"
    BUILDKITE = "buildkite"
    CIRCLECI = "circleci"
    TRAVIS = "travis"
    DRONE = "drone"
    
    ALL = [GITHUB, GITLAB, JENKINS, BUILDKITE, CIRCLECI, TRAVIS, DRONE]


class CloudProvider:
    """Supported cloud providers."""
    
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    HEROKU = "heroku"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    
    ALL = [AWS, GCP, AZURE, HEROKU, DOCKER, KUBERNETES]


class Framework:
    """Supported frameworks."""
    
    # Python
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    STARLETTE = "starlette"
    
    # Node
    EXPRESS = "express"
    NEXTJS = "nextjs"
    REMIX = "remix"
    NUXT = "nuxt"
    ASTRO = "astro"
    
    # Go
    GIN = "gin"
    ECHO = "echo"
    CHI = "chi"
    
    # CLI/Libraries
    CLI = "cli"
    LIBRARY = "library"
    GENERIC = "generic"
    
    ALL = [FASTAPI, DJANGO, FLASK, STARLETTE, EXPRESS, NEXTJS, REMIX, NUXT, ASTRO, GIN, ECHO, CHI, CLI, LIBRARY, GENERIC]
