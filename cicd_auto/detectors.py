"""Project detection logic for each dimension."""

import json
import re
from pathlib import Path
from typing import Optional

import yaml

from .models import Framework, Language, PackageManager, Platform, TestFramework


class LanguageDetector:
    """Detect programming language."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self) -> Optional[str]:
        """Detect language from project files."""
        # Python
        if self._check_python():
            return Language.PYTHON
        
        # Node
        if self._check_node():
            return Language.NODE
        
        # Go
        if self._check_go():
            return Language.GO
        
        # Rust
        if self._check_rust():
            return Language.RUST
        
        # Java
        if self._check_java():
            return Language.JAVA
        
        # C#
        if self._check_csharp():
            return Language.CSHARP
        
        # Ruby
        if self._check_ruby():
            return Language.RUBY
        
        # PHP
        if self._check_php():
            return Language.PHP
        
        return None

    def _check_python(self) -> bool:
        """Check for Python project markers."""
        python_files = [
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "uv.lock",
        ]
        return any((self.repo_path / f).exists() for f in python_files)

    def _check_node(self) -> bool:
        """Check for Node.js project markers."""
        return (self.repo_path / "package.json").exists()

    def _check_go(self) -> bool:
        """Check for Go project markers."""
        return (self.repo_path / "go.mod").exists()

    def _check_rust(self) -> bool:
        """Check for Rust project markers."""
        return (self.repo_path / "Cargo.toml").exists()

    def _check_java(self) -> bool:
        """Check for Java project markers."""
        return (self.repo_path / "pom.xml").exists() or (self.repo_path / "build.gradle").exists()

    def _check_csharp(self) -> bool:
        """Check for C# project markers."""
        csharp_files = [".csproj", ".sln", "Directory.Build.props"]
        return any(self.repo_path.glob(f"**/*{f}"))

    def _check_ruby(self) -> bool:
        """Check for Ruby project markers."""
        return (self.repo_path / "Gemfile").exists()

    def _check_php(self) -> bool:
        """Check for PHP project markers."""
        return (self.repo_path / "composer.json").exists()


class PackageManagerDetector:
    """Detect package manager."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self, language: Optional[str] = None) -> Optional[str]:
        """Detect package manager."""
        if language == Language.PYTHON:
            return self._detect_python_pm()
        elif language == Language.NODE:
            return self._detect_node_pm()
        elif language == Language.GO:
            return self._detect_go_pm()
        elif language == Language.RUST:
            return PackageManager.CARGO
        elif language == Language.RUBY:
            return PackageManager.BUNDLER
        elif language == Language.JAVA:
            return self._detect_java_pm()
        
        return None

    def _detect_python_pm(self) -> Optional[str]:
        """Detect Python package manager."""
        # Check in order of preference
        if (self.repo_path / "uv.lock").exists():
            return PackageManager.UV
        if (self.repo_path / "poetry.lock").exists():
            return PackageManager.POETRY
        if (self.repo_path / "Pipfile.lock").exists():
            return PackageManager.PIPENV
        if (self.repo_path / "requirements.txt").exists():
            return PackageManager.PIP
        if (self.repo_path / "pyproject.toml").exists():
            # Check pyproject.toml for tool config
            toml_file = self.repo_path / "pyproject.toml"
            try:
                content = toml_file.read_text()
                if "[tool.poetry]" in content:
                    return PackageManager.POETRY
                if "[tool.pdm]" in content:
                    return "pdm"
                if "[tool.uv]" in content or "[project]" in content:
                    # Assume uv if pyproject.toml with [project]
                    return PackageManager.UV
            except Exception:
                pass
        
        return PackageManager.PIP  # Default fallback

    def _detect_node_pm(self) -> Optional[str]:
        """Detect Node.js package manager."""
        if (self.repo_path / "pnpm-lock.yaml").exists():
            return PackageManager.PNPM
        if (self.repo_path / "yarn.lock").exists():
            return PackageManager.YARN
        if (self.repo_path / "bun.lockb").exists():
            return PackageManager.BUN
        return PackageManager.NPM  # Default

    def _detect_go_pm(self) -> Optional[str]:
        """Detect Go package manager."""
        if (self.repo_path / "go.mod").exists():
            return PackageManager.MOD
        return PackageManager.GOPATH

    def _detect_java_pm(self) -> Optional[str]:
        """Detect Java package manager."""
        if (self.repo_path / "pom.xml").exists():
            return PackageManager.MAVEN
        if (self.repo_path / "build.gradle").exists() or (self.repo_path / "build.gradle.kts").exists():
            return PackageManager.GRADLE
        return None


class TestFrameworkDetector:
    """Detect test framework."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self, language: Optional[str] = None) -> Optional[str]:
        """Detect test framework."""
        if language == Language.PYTHON:
            return self._detect_python_tests()
        elif language == Language.NODE:
            return self._detect_node_tests()
        elif language == Language.GO:
            return TestFramework.GO_TEST
        elif language == Language.RUST:
            return TestFramework.CARGO_TEST
        
        return None

    def _detect_python_tests(self) -> Optional[str]:
        """Detect Python test framework."""
        # Check pyproject.toml
        toml_file = self.repo_path / "pyproject.toml"
        if toml_file.exists():
            try:
                content = toml_file.read_text()
                if "pytest" in content:
                    return TestFramework.PYTEST
                if "nose2" in content:
                    return TestFramework.NOSE2
            except Exception:
                pass
        
        # Check requirements files
        for req_file in ["requirements-dev.txt", "requirements.txt", "setup.py"]:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text()
                    if "pytest" in content:
                        return TestFramework.PYTEST
                    if "nose2" in content:
                        return TestFramework.NOSE2
                except Exception:
                    pass
        
        # Check tests directory for test files
        tests_dir = self.repo_path / "tests"
        if tests_dir.exists():
            # If tests/ exists, assume pytest (most common)
            return TestFramework.PYTEST
        
        # Check test_*.py files at root
        if any(self.repo_path.glob("test_*.py")):
            return TestFramework.PYTEST
        
        return TestFramework.PYTEST  # Default for Python

    def _detect_node_tests(self) -> Optional[str]:
        """Detect Node.js test framework."""
        pkg_json = self.repo_path / "package.json"
        if pkg_json.exists():
            try:
                content = json.loads(pkg_json.read_text())
                deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}
                
                if "jest" in deps:
                    return TestFramework.JEST
                if "mocha" in deps:
                    return TestFramework.MOCHA
                if "vitest" in deps:
                    return TestFramework.VITEST
            except Exception:
                pass
        
        return TestFramework.JEST  # Default


class PlatformDetector:
    """Detect CI/CD platform."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self) -> Optional[str]:
        """Detect CI/CD platform."""
        # GitHub Actions
        if (self.repo_path / ".github" / "workflows").exists():
            return Platform.GITHUB
        
        # GitLab CI
        if (self.repo_path / ".gitlab-ci.yml").exists():
            return Platform.GITLAB
        
        # Jenkins
        if (self.repo_path / "Jenkinsfile").exists():
            return Platform.JENKINS
        
        # Buildkite
        if (self.repo_path / ".buildkite").exists():
            return Platform.BUILDKITE
        
        # CircleCI
        if (self.repo_path / ".circleci" / "config.yml").exists():
            return Platform.CIRCLECI
        
        # Travis CI
        if (self.repo_path / ".travis.yml").exists():
            return Platform.TRAVIS
        
        # Drone
        if (self.repo_path / ".drone.yml").exists():
            return Platform.DRONE
        
        # Default to GitHub (most common)
        if (self.repo_path / ".git").exists():
            return Platform.GITHUB
        
        return None


class FrameworkDetector:
    """Detect web/app framework."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self, language: Optional[str] = None) -> Optional[str]:
        """Detect framework."""
        if language == Language.PYTHON:
            return self._detect_python_framework()
        elif language == Language.NODE:
            return self._detect_node_framework()
        elif language == Language.GO:
            return self._detect_go_framework()
        
        return Framework.GENERIC

    def _detect_python_framework(self) -> Optional[str]:
        """Detect Python framework."""
        # Check imports in Python files
        for py_file in self.repo_path.glob("**/*.py"):
            if py_file.name.startswith("test_"):
                continue
            try:
                content = py_file.read_text()
                if "fastapi" in content or "from fastapi" in content:
                    return Framework.FASTAPI
                if "django" in content or "from django" in content:
                    return Framework.DJANGO
                if "flask" in content or "from flask" in content:
                    return Framework.FLASK
                if "starlette" in content or "from starlette" in content:
                    return Framework.STARLETTE
            except Exception:
                pass
        
        # Check pyproject.toml
        toml_file = self.repo_path / "pyproject.toml"
        if toml_file.exists():
            try:
                content = toml_file.read_text()
                if "fastapi" in content:
                    return Framework.FASTAPI
                if "django" in content:
                    return Framework.DJANGO
                if "flask" in content:
                    return Framework.FLASK
            except Exception:
                pass
        
        # Check for main.py / app.py patterns
        if (self.repo_path / "main.py").exists():
            return Framework.FASTAPI
        if (self.repo_path / "app.py").exists():
            return Framework.FLASK
        if (self.repo_path / "manage.py").exists():
            return Framework.DJANGO
        
        return Framework.GENERIC

    def _detect_node_framework(self) -> Optional[str]:
        """Detect Node.js framework."""
        pkg_json = self.repo_path / "package.json"
        if pkg_json.exists():
            try:
                content = json.loads(pkg_json.read_text())
                deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}
                
                if "next" in deps:
                    return Framework.NEXTJS
                if "nuxt" in deps:
                    return Framework.NUXT
                if "remix" in deps:
                    return Framework.REMIX
                if "astro" in deps:
                    return Framework.ASTRO
                if "express" in deps:
                    return Framework.EXPRESS
            except Exception:
                pass
        
        return Framework.GENERIC

    def _detect_go_framework(self) -> Optional[str]:
        """Detect Go framework."""
        go_files = list(self.repo_path.glob("**/*.go"))
        if not go_files:
            return Framework.GENERIC
        
        for go_file in go_files[:5]:  # Check first 5 files
            try:
                content = go_file.read_text()
                if "github.com/gin-gonic/gin" in content:
                    return Framework.GIN
                if "github.com/labstack/echo" in content:
                    return Framework.ECHO
                if "github.com/go-chi/chi" in content:
                    return Framework.CHI
            except Exception:
                pass
        
        return Framework.CLI  # Default for Go


class CloudDetector:
    """Detect cloud provider/deployment target."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self) -> Optional[str]:
        """Detect cloud provider."""
        # Docker
        if (self.repo_path / "Dockerfile").exists():
            # Check if pushed to registries
            if self._check_dockerfile_registry():
                return "docker"
        
        # Kubernetes
        if (self.repo_path / "k8s").exists() or any(self.repo_path.glob("**/k8s/*.yml")):
            return "kubernetes"
        if (self.repo_path / "helm").exists():
            return "kubernetes"
        
        # Terraform (multi-cloud, but indicates IaC)
        if any(self.repo_path.glob("**/*.tf")):
            if self._check_terraform_aws():
                return "aws"
            if self._check_terraform_gcp():
                return "gcp"
            if self._check_terraform_azure():
                return "azure"
        
        # CloudFormation (AWS)
        if any(self.repo_path.glob("**/template.yml")) or any(self.repo_path.glob("**/template.json")):
            return "aws"
        
        # AWS specific
        if (self.repo_path / "serverless.yml").exists():
            return "aws"
        
        # Heroku
        if (self.repo_path / "Procfile").exists():
            return "heroku"
        
        return None

    def _check_dockerfile_registry(self) -> bool:
        """Check if Dockerfile mentions registry."""
        dockerfile = self.repo_path / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text().lower()
            registries = ["gcr.io", "ecr", "docker.io", "quay.io", "artifactory"]
            return any(reg in content for reg in registries)
        return False

    def _check_terraform_aws(self) -> bool:
        """Check if terraform files are AWS."""
        for tf_file in self.repo_path.glob("**/*.tf"):
            try:
                content = tf_file.read_text()
                if "aws_" in content or "provider \"aws\"" in content:
                    return True
            except Exception:
                pass
        return False

    def _check_terraform_gcp(self) -> bool:
        """Check if terraform files are GCP."""
        for tf_file in self.repo_path.glob("**/*.tf"):
            try:
                content = tf_file.read_text()
                if "google_" in content or "provider \"google\"" in content:
                    return True
            except Exception:
                pass
        return False

    def _check_terraform_azure(self) -> bool:
        """Check if terraform files are Azure."""
        for tf_file in self.repo_path.glob("**/*.tf"):
            try:
                content = tf_file.read_text()
                if "azurerm_" in content or "provider \"azurerm\"" in content:
                    return True
            except Exception:
                pass
        return False


class PythonVersionDetector:
    """Detect Python version constraints."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def detect(self) -> Optional[str]:
        """Detect minimum Python version."""
        # Check pyproject.toml
        toml_file = self.repo_path / "pyproject.toml"
        if toml_file.exists():
            try:
                content = toml_file.read_text()
                # Look for requires-python
                match = re.search(r'requires-python\s*=\s*"([^"]+)"', content)
                if match:
                    version_spec = match.group(1)
                    # Extract version: ">=3.11", "3.11+", etc.
                    versions = re.findall(r'3\.\d+', version_spec)
                    if versions:
                        return versions[0]
            except Exception:
                pass
        
        # Default to 3.11
        return "3.11"
