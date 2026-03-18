"""Tests for project analyzer."""

import tempfile
from pathlib import Path

import pytest

from cicd_auto.analyzer import ProjectAnalyzer


@pytest.fixture
def temp_repo():
    """Create a temporary repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestLanguageDetection:
    """Test language detection."""

    def test_detect_python_project(self, temp_repo):
        """Detect Python project."""
        (temp_repo / "pyproject.toml").write_text("[project]\nname = 'test'")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.language == "python"

    def test_detect_node_project(self, temp_repo):
        """Detect Node.js project."""
        (temp_repo / "package.json").write_text('{"name": "test"}')
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.language == "node"

    def test_detect_go_project(self, temp_repo):
        """Detect Go project."""
        (temp_repo / "go.mod").write_text("module example.com/test")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.language == "go"

    def test_detect_rust_project(self, temp_repo):
        """Detect Rust project."""
        (temp_repo / "Cargo.toml").write_text('[package]\nname = "test"')
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.language == "rust"


class TestPackageManagerDetection:
    """Test package manager detection."""

    def test_detect_uv(self, temp_repo):
        """Detect uv."""
        (temp_repo / "uv.lock").write_text("")
        (temp_repo / "pyproject.toml").write_text("[project]")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.package_manager == "uv"

    def test_detect_poetry(self, temp_repo):
        """Detect Poetry."""
        (temp_repo / "poetry.lock").write_text("")
        (temp_repo / "pyproject.toml").write_text("[tool.poetry]")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.package_manager == "poetry"

    def test_detect_npm(self, temp_repo):
        """Detect npm."""
        (temp_repo / "package.json").write_text('{"name": "test"}')
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.package_manager == "npm"

    def test_detect_cargo(self, temp_repo):
        """Detect Cargo."""
        (temp_repo / "Cargo.toml").write_text('[package]\nname = "test"')
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.package_manager == "cargo"


class TestTestFrameworkDetection:
    """Test test framework detection."""

    def test_detect_pytest(self, temp_repo):
        """Detect pytest."""
        (temp_repo / "pyproject.toml").write_text("[project]\ndependencies = ['pytest']")
        (temp_repo / "tests").mkdir()
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.test_framework == "pytest"

    def test_detect_jest(self, temp_repo):
        """Detect Jest."""
        package_json = {
            "name": "test",
            "devDependencies": {"jest": "^29.0.0"}
        }
        import json
        (temp_repo / "package.json").write_text(json.dumps(package_json))
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.test_framework == "jest"


class TestPlatformDetection:
    """Test platform detection."""

    def test_detect_github_actions(self, temp_repo):
        """Detect GitHub Actions."""
        (temp_repo / ".github" / "workflows").mkdir(parents=True)
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.platform == "github"

    def test_detect_gitlab_ci(self, temp_repo):
        """Detect GitLab CI."""
        (temp_repo / ".gitlab-ci.yml").write_text("")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.platform == "gitlab"

    def test_detect_jenkins(self, temp_repo):
        """Detect Jenkins."""
        (temp_repo / "Jenkinsfile").write_text("")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.platform == "jenkins"


class TestCommandInference:
    """Test command inference."""

    def test_infer_pytest_command_with_uv(self, temp_repo):
        """Infer pytest command with uv."""
        (temp_repo / "uv.lock").write_text("")
        (temp_repo / "pyproject.toml").write_text("[project]")
        (temp_repo / "tests").mkdir()
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.test_command == "uv run pytest"

    def test_infer_npm_test_command(self, temp_repo):
        """Infer npm test command."""
        (temp_repo / "package.json").write_text('{"name": "test"}')
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.test_command == "npm test"

    def test_infer_go_test_command(self, temp_repo):
        """Infer go test command."""
        (temp_repo / "go.mod").write_text("module test")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.test_command == "go test ./..."


class TestBuildDetection:
    """Test build/deployment detection."""

    def test_detect_dockerfile(self, temp_repo):
        """Detect Dockerfile."""
        (temp_repo / "Dockerfile").write_text("FROM python:3.11")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.has_dockerfile

    def test_detect_terraform(self, temp_repo):
        """Detect Terraform."""
        (temp_repo / "main.tf").write_text("resource")
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.has_terraform

    def test_detect_k8s(self, temp_repo):
        """Detect Kubernetes."""
        (temp_repo / "k8s").mkdir()
        analyzer = ProjectAnalyzer(str(temp_repo))
        analysis = analyzer.analyze()
        assert analysis.has_k8s
