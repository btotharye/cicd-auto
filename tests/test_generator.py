"""Tests for workflow generator."""

import tempfile
from pathlib import Path

import pytest

from cicd_auto.analyzer import ProjectAnalyzer
from cicd_auto.generator import DependabotGenerator, PreCommitGenerator, WorkflowGenerator


@pytest.fixture
def python_analysis():
    """Create a Python project analysis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "pyproject.toml").write_text("[project]\nname = 'test'")
        (tmpdir / "uv.lock").write_text("")
        (tmpdir / "tests").mkdir()
        
        analyzer = ProjectAnalyzer(str(tmpdir))
        yield analyzer.analyze()


@pytest.fixture
def node_analysis():
    """Create a Node.js project analysis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "package.json").write_text('{"name": "test", "devDependencies": {"jest": "^29.0.0"}}')
        
        analyzer = ProjectAnalyzer(str(tmpdir))
        yield analyzer.analyze()


@pytest.fixture
def go_analysis():
    """Create a Go project analysis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "go.mod").write_text("module example.com/test")
        
        analyzer = ProjectAnalyzer(str(tmpdir))
        yield analyzer.analyze()


class TestWorkflowGenerator:
    """Test workflow generation."""

    def test_generate_github_ci_python(self, python_analysis):
        """Generate GitHub CI for Python."""
        generator = WorkflowGenerator()
        workflows = generator.generate_github_workflows(python_analysis)
        
        assert ".github/workflows/ci.yml" in workflows
        assert "pytest" in workflows[".github/workflows/ci.yml"]
        assert "uv run" in workflows[".github/workflows/ci.yml"]

    def test_generate_github_ci_node(self, node_analysis):
        """Generate GitHub CI for Node."""
        generator = WorkflowGenerator()
        workflows = generator.generate_github_workflows(node_analysis)
        
        assert ".github/workflows/ci.yml" in workflows
        assert "npm test" in workflows[".github/workflows/ci.yml"] or "npm ci" in workflows[".github/workflows/ci.yml"]

    def test_generate_github_ci_go(self, go_analysis):
        """Generate GitHub CI for Go."""
        generator = WorkflowGenerator()
        workflows = generator.generate_github_workflows(go_analysis)
        
        assert ".github/workflows/ci.yml" in workflows
        assert "go test" in workflows[".github/workflows/ci.yml"]

    def test_generate_gitlab_ci_python(self, python_analysis):
        """Generate GitLab CI for Python."""
        generator = WorkflowGenerator()
        workflows = generator.generate_gitlab_workflows(python_analysis)
        
        assert ".gitlab-ci.yml" in workflows
        content = workflows[".gitlab-ci.yml"]
        assert "stages:" in content
        assert "pytest" in content or "test" in content

    def test_generate_jenkins_python(self, python_analysis):
        """Generate Jenkins Jenkinsfile for Python."""
        generator = WorkflowGenerator()
        workflows = generator.generate_jenkins_workflows(python_analysis)
        
        assert "Jenkinsfile" in workflows
        content = workflows["Jenkinsfile"]
        assert "pipeline" in content
        assert "python" in content.lower()

    def test_generate_buildkite_python(self, python_analysis):
        """Generate Buildkite pipeline for Python."""
        generator = WorkflowGenerator()
        workflows = generator.generate_buildkite_workflows(python_analysis)
        
        assert ".buildkite/pipeline.yml" in workflows
        content = workflows[".buildkite/pipeline.yml"]
        assert "steps:" in content


class TestPreCommitGenerator:
    """Test pre-commit generator."""

    def test_generate_pre_commit_python(self, python_analysis):
        """Generate pre-commit config for Python."""
        generator = PreCommitGenerator()
        config = generator.generate_pre_commit_config(python_analysis)
        
        assert config is not None
        assert "ruff" in config
        assert "mypy" in config

    def test_generate_pre_commit_node(self, node_analysis):
        """Pre-commit not needed for Node."""
        generator = PreCommitGenerator()
        config = generator.generate_pre_commit_config(node_analysis)
        
        assert config is None


class TestDependabotGenerator:
    """Test Dependabot generator."""

    def test_generate_dependabot_python(self, python_analysis):
        """Generate Dependabot config for Python."""
        generator = DependabotGenerator()
        config = generator.generate_dependabot_config(python_analysis)
        
        assert config is not None
        assert "pip" in config
        assert "version: 2" in config

    def test_generate_dependabot_node(self, node_analysis):
        """Generate Dependabot config for Node."""
        generator = DependabotGenerator()
        config = generator.generate_dependabot_config(node_analysis)
        
        assert config is not None
        assert "npm" in config

    def test_generate_dependabot_go(self, go_analysis):
        """Generate Dependabot config for Go."""
        generator = DependabotGenerator()
        config = generator.generate_dependabot_config(go_analysis)
        
        assert config is not None
        assert "gomod" in config
