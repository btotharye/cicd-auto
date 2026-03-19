"""Generate CI/CD workflows from templates and analysis."""

from pathlib import Path
from typing import Dict, Optional

import jinja2
import yaml

from .models import ProjectAnalysis


class WorkflowGenerator:
    """Generate CI/CD workflows from templates."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            keep_trailing_newline=True,
        )

    def generate_github_workflows(self, analysis: ProjectAnalysis) -> Dict[str, str]:
        """Generate GitHub Actions workflows."""
        workflows = {}

        # Generate CI workflow
        ci_workflow = self._generate_github_ci(analysis)
        if ci_workflow:
            workflows[".github/workflows/ci.yml"] = ci_workflow

        # Generate CD workflow
        cd_workflow = self._generate_github_cd(analysis)
        if cd_workflow:
            workflows[".github/workflows/cd.yml"] = cd_workflow

        return workflows

    def generate_gitlab_workflows(self, analysis: ProjectAnalysis) -> Dict[str, str]:
        """Generate GitLab CI workflows."""
        workflows = {}

        # GitLab uses single .gitlab-ci.yml
        gitlab_ci = self._generate_gitlab_ci(analysis)
        if gitlab_ci:
            workflows[".gitlab-ci.yml"] = gitlab_ci

        return workflows

    def generate_jenkins_workflows(self, analysis: ProjectAnalysis) -> Dict[str, str]:
        """Generate Jenkins Jenkinsfile."""
        workflows = {}

        jenkinsfile = self._generate_jenkinsfile(analysis)
        if jenkinsfile:
            workflows["Jenkinsfile"] = jenkinsfile

        return workflows

    def generate_buildkite_workflows(self, analysis: ProjectAnalysis) -> Dict[str, str]:
        """Generate Buildkite pipeline."""
        workflows = {}

        pipeline = self._generate_buildkite_pipeline(analysis)
        if pipeline:
            workflows[".buildkite/pipeline.yml"] = pipeline

        return workflows

    def _generate_github_ci(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate GitHub Actions CI workflow."""
        if not analysis.language:
            return None

        template_name = f"github/{analysis.language}_ci.yml"
        if not (self.templates_dir / template_name).exists():
            return None

        context = self._build_context(analysis)
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _generate_github_cd(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate GitHub Actions CD workflow."""
        if not analysis.language:
            return None

        template_name = f"github/{analysis.language}_cd.yml"
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            # Some languages might not have CD templates
            return None

        try:
            context = self._build_context(analysis)
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception:
            return None

    def _generate_gitlab_ci(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate GitLab CI workflow."""
        if not analysis.language:
            return None

        template_name = f"gitlab/{analysis.language}_ci.yml"
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            return None

        context = self._build_context(analysis)
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _generate_jenkinsfile(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate Jenkins Jenkinsfile."""
        if not analysis.language:
            return None

        template_name = "jenkins/Jenkinsfile.groovy"
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            return None

        context = self._build_context(analysis)
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _generate_buildkite_pipeline(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate Buildkite pipeline."""
        if not analysis.language:
            return None

        template_name = "buildkite/pipeline.yml"
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            return None

        context = self._build_context(analysis)
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _build_context(self, analysis: ProjectAnalysis) -> Dict:
        """Build template context from analysis."""
        context = {
            "language": analysis.language,
            "framework": analysis.framework,
            "package_manager": analysis.package_manager,
            "test_framework": analysis.test_framework,
            "test_command": analysis.test_command,
            "lint_command": analysis.lint_command,
            "build_command": analysis.build_command,
            "python_versions": self._get_python_versions(analysis),
            "node_versions": self._get_node_versions(analysis),
            "go_versions": self._get_go_versions(analysis),
            "notify_email": "ops@example.com",  # TODO: Make configurable
        }
        return context

    def _get_python_versions(self, analysis: ProjectAnalysis) -> list:
        """Get Python versions to test against."""
        if analysis.language != "python":
            return []

        # If specific version detected, test current + next
        if analysis.python_version:
            major, minor = analysis.python_version.split(".")
            return [analysis.python_version, f"{major}.{int(minor) + 1}"]

        # Default to recent versions
        return ["3.11", "3.12"]

    def _get_node_versions(self, analysis: ProjectAnalysis) -> list:
        """Get Node.js versions to test against."""
        if analysis.language != "node":
            return []

        # Default to LTS versions
        return ["18", "20"]

    def _get_go_versions(self, analysis: ProjectAnalysis) -> list:
        """Get Go versions to test against."""
        if analysis.language != "go":
            return []

        # Default to recent versions
        return ["1.21", "1.22"]


class PreCommitGenerator:
    """Generate pre-commit configuration."""

    def generate_pre_commit_config(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate .pre-commit-config.yaml."""
        if analysis.language != "python":
            return None

        config = {
            "repos": [
                {
                    "repo": "https://github.com/astral-sh/ruff-pre-commit",
                    "rev": "v0.1.13",
                    "hooks": [
                        {"id": "ruff", "args": ["--fix"]},
                        {"id": "ruff-format"},
                    ],
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.7.1",
                    "hooks": [{"id": "mypy"}],
                },
                {
                    "repo": "https://github.com/compilerla/conventional-pre-commit",
                    "rev": "v2.4.0",
                    "hooks": [{"id": "conventional-pre-commit", "stages": ["commit-msg"]}],
                },
            ]
        }

        return yaml.dump(config, default_flow_style=False, sort_keys=False)


class DependabotGenerator:
    """Generate Dependabot configuration."""

    def generate_dependabot_config(self, analysis: ProjectAnalysis) -> Optional[str]:
        """Generate .github/dependabot.yml."""
        ecosystems = []

        if analysis.language == "python":
            ecosystems.append({"package-ecosystem": "pip", "directory": "/"})
        elif analysis.language == "node":
            ecosystems.append({"package-ecosystem": "npm", "directory": "/"})
        elif analysis.language == "go":
            ecosystems.append({"package-ecosystem": "gomod", "directory": "/"})
        elif analysis.language == "rust":
            ecosystems.append({"package-ecosystem": "cargo", "directory": "/"})

        if analysis.has_dockerfile:
            ecosystems.append({"package-ecosystem": "docker", "directory": "/"})

        if not ecosystems:
            return None

        config = {
            "version": 2,
            "updates": [
                {
                    **eco,
                    "schedule": {"interval": "weekly", "day": "monday"},
                    "commit-message": {"prefix": "chore: ", "prefix-scope": "deps"},
                }
                for eco in ecosystems
            ],
        }

        return yaml.dump(config, default_flow_style=False, sort_keys=False)
