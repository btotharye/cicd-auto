"""Main project analyzer - orchestrates all detectors."""

from pathlib import Path

from .detectors import (
    CloudDetector,
    FrameworkDetector,
    LanguageDetector,
    PackageManagerDetector,
    PlatformDetector,
    PythonVersionDetector,
    TestFrameworkDetector,
)
from .models import ProjectAnalysis


class ProjectAnalyzer:
    """Analyze a project and detect its configuration."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        
        # Initialize detectors
        self.language_detector = LanguageDetector(repo_path)
        self.package_manager_detector = PackageManagerDetector(repo_path)
        self.test_framework_detector = TestFrameworkDetector(repo_path)
        self.platform_detector = PlatformDetector(repo_path)
        self.framework_detector = FrameworkDetector(repo_path)
        self.cloud_detector = CloudDetector(repo_path)
        self.python_version_detector = PythonVersionDetector(repo_path)

    def analyze(self) -> ProjectAnalysis:
        """Run full project analysis."""
        # Detect language first (everything else depends on it)
        language = self.language_detector.detect()
        
        # Then detect everything else
        package_manager = self.package_manager_detector.detect(language)
        test_framework = self.test_framework_detector.detect(language)
        platform = self.platform_detector.detect()
        framework = self.framework_detector.detect(language)
        cloud = self.cloud_detector.detect()
        
        # Language-specific
        python_version = None
        if language == "python":
            python_version = self.python_version_detector.detect()
        
        # Detect build info
        has_dockerfile = (self.repo_path / "Dockerfile").exists()
        has_terraform = any(self.repo_path.glob("**/*.tf"))
        has_k8s = (self.repo_path / "k8s").exists() or any(self.repo_path.glob("**/k8s/*.yml"))
        
        # Infer commands
        test_command = self._infer_test_command(language, test_framework, package_manager)
        lint_command = self._infer_lint_command(language, package_manager)
        build_command = self._infer_build_command(language, package_manager)
        
        # Build analysis
        analysis = ProjectAnalysis(
            language=language,
            framework=framework,
            package_manager=package_manager,
            test_framework=test_framework,
            platform=platform,
            cloud=cloud,
            has_dockerfile=has_dockerfile,
            has_terraform=has_terraform,
            has_k8s=has_k8s,
            test_command=test_command,
            lint_command=lint_command,
            build_command=build_command,
            python_version=python_version,
        )
        
        return analysis

    def _infer_test_command(
        self, language: str, test_framework: str, package_manager: str
    ) -> str:
        """Infer the test command."""
        if language == "python":
            if test_framework == "pytest":
                if package_manager == "uv":
                    return "uv run pytest"
                elif package_manager == "poetry":
                    return "poetry run pytest"
                return "pytest"
            elif test_framework == "unittest":
                return "python -m unittest"
            return "pytest"  # Default
        
        elif language == "node":
            if package_manager == "pnpm":
                return "pnpm test"
            elif package_manager == "yarn":
                return "yarn test"
            elif package_manager == "bun":
                return "bun test"
            return "npm test"
        
        elif language == "go":
            return "go test ./..."
        
        elif language == "rust":
            return "cargo test"
        
        return ""

    def _infer_lint_command(self, language: str, package_manager: str) -> str:
        """Infer the lint command."""
        if language == "python":
            if package_manager == "uv":
                return "uv run ruff check ."
            elif package_manager == "poetry":
                return "poetry run ruff check ."
            return "ruff check ."
        
        elif language == "node":
            if package_manager == "pnpm":
                return "pnpm lint"
            elif package_manager == "yarn":
                return "yarn lint"
            elif package_manager == "bun":
                return "bun run lint"
            return "npm run lint"
        
        elif language == "go":
            return "go fmt ./... && go vet ./..."
        
        elif language == "rust":
            return "cargo clippy -- -D warnings"
        
        return ""

    def _infer_build_command(self, language: str, package_manager: str) -> str:
        """Infer the build command."""
        if language == "python":
            if package_manager == "uv":
                return "uv build"
            elif package_manager == "poetry":
                return "poetry build"
            return "python -m build"
        
        elif language == "node":
            if package_manager == "pnpm":
                return "pnpm build"
            elif package_manager == "yarn":
                return "yarn build"
            elif package_manager == "bun":
                return "bun run build"
            return "npm run build"
        
        elif language == "go":
            return "go build -o app ."
        
        elif language == "rust":
            return "cargo build --release"
        
        return ""
