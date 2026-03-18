# 🚀 cicd-auto

> Auto-generate production-ready CI/CD pipelines for any project

Tired of copy-pasting CI/CD configs? **cicd-auto** analyzes your project and generates sensible, best-practice workflows for GitHub Actions, GitLab CI, Jenkins, Buildkite, and more.

```bash
# Analyze your project
cicd-auto analyze

# Generate workflows
cicd-auto generate --platform github,gitlab

# Done. Push and merge.
```

---

## Features

- ✅ **Smart Detection**: Automatically detects language, framework, package manager, test framework
- ✅ **Multi-Platform**: GitHub Actions, GitLab CI, Jenkins, Buildkite, CircleCI, Drone
- ✅ **Best Practices**: Production-grade workflows with linting, testing, coverage, security scanning
- ✅ **Zero Config**: Works out of the box
- ✅ **Extensible**: Easy to customize or add new platforms/languages
- ✅ **AI-Ready**: Claude integration for edge cases (Phase 2)

**Supported Languages:**
- Python (uv, Poetry, pip)
- Node.js (npm, yarn, pnpm, bun)
- Go (go mod)
- Rust (Cargo)
- Java, C#, Ruby, PHP (coming soon)

---

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv pip install cicd-auto

# Using pip
pip install cicd-auto
```

### Usage

```bash
# Analyze current project
cicd-auto analyze

# Shows detected stack:
# ┌─────────────────────┐
# │ Language      Python
# │ Framework     FastAPI
# │ Package Mgr   uv
# │ Tests         pytest
# │ Platform      GitHub Actions
# └─────────────────────┘
```

```bash
# Generate workflows
cicd-auto generate

# Creates:
# - .github/workflows/ci.yml
# - .github/workflows/cd.yml
# - .pre-commit-config.yaml
# - .github/dependabot.yml
```

```bash
# Preview without writing
cicd-auto generate --dry-run

# Generate for specific platforms
cicd-auto generate --platform github,gitlab

# Generate and commit to branch
cicd-auto generate --branch feat/auto-cicd
```

---

## What Gets Generated

### CI Workflow (GitHub Actions)

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Set Python version
        run: uv python pin ${{ matrix.python-version }}
      - name: Install dependencies
        run: uv sync
      - name: Lint
        run: uv run ruff check .
      - name: Type check
        run: uv run mypy .
      - name: Test
        run: uv run pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### CD Workflow (Docker → Registry)

```yaml
name: CD

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v2
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v2.4.0
    hooks:
      - id: conventional-pre-commit
```

### Dependabot Config

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    commit-message:
      prefix: "chore: "
```

---

## Advanced Usage

### Custom Platforms

```bash
# Generate for multiple platforms
cicd-auto generate --platform github gitlab jenkins

# Platform-specific options
cicd-auto generate --platform jenkins --jenkins-agent docker
```

### With Claude Integration (Phase 2)

```bash
# Let Claude ask clarifying questions
cicd-auto generate --interactive

# Claude might ask:
# "I detected FastAPI + uv. Do you want:
#  - ASGI deployment? [uvicorn/gunicorn]
#  - Docker registry? [ECR/GCR/GHCR]
#  - Database migrations? [yes/no]"
```

### Dry Run + Diff

```bash
# See what would be generated
cicd-auto generate --dry-run

# See diff from current config
cicd-auto generate --dry-run --diff
```

---

## Configuration

### Via File

Create `.cicd-auto/config.json`:

```json
{
  "version": "1.0",
  "platforms": ["github", "gitlab"],
  "languages": ["python", "node"],
  "matrix": {
    "python-versions": ["3.11", "3.12"],
    "node-versions": ["18", "20"]
  },
  "services": {
    "postgres": true,
    "redis": false
  },
  "deploy": {
    "enabled": true,
    "registry": "ghcr.io",
    "cluster": "kubernetes"
  }
}
```

### Via CLI

```bash
cicd-auto config set platforms github,gitlab
cicd-auto config set matrix.python-versions 3.11,3.12
cicd-auto config show
```

---

## Development

### Setup

```bash
git clone https://github.com/btotharye/cicd-auto.git
cd cicd-auto

# Using Makefile (easiest)
make install-dev
make test

# Or using uv
uv sync --with dev
uv run pytest
```

### Testing

```bash
# Run all tests
make test

# Run specific test
uv run pytest tests/test_analyzer.py::TestLanguageDetection -v

# With coverage
uv run pytest --cov=cicd_auto
```

### Adding Support for New Language/Platform

1. Add detector class to `cicd_auto/detectors.py`
2. Register in `ProjectAnalyzer`
3. Create template in `templates/<language>/<platform>/`
4. Add tests to `tests/test_analyzer.py`
5. Update README

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Roadmap

### Phase 1 (MVP) - In Progress ✅
- [x] Language detection (Python, Node, Go, Rust)
- [x] Package manager detection
- [x] Test framework detection
- [x] Platform detection
- [x] CLI `analyze` command
- [ ] Workflow template generation
- [ ] GitHub Actions support
- [ ] Tests + documentation

### Phase 2 - Next
- [ ] Claude integration for edge cases
- [ ] More platforms (GitLab, Jenkins, Buildkite)
- [ ] CD/deployment workflows
- [ ] Pre-commit hook generation
- [ ] Dependabot configuration

### Phase 3 - Future
- [ ] GitHub Action wrapper (one-click setup)
- [ ] Web UI for visual builder
- [ ] Integration marketplace
- [ ] Community template sharing
- [ ] Advanced optimization suggestions

### Phase 4+ - Later
- [ ] Kubernetes manifests
- [ ] Terraform modules
- [ ] Docker image optimization
- [ ] Performance analytics
- [ ] SaaS version

---

## FAQ

**Q: Will this overwrite my existing CI/CD?**  
A: No. Use `--dry-run` first to preview. Generated files go to a branch (`feat/auto-cicd` by default).

**Q: What if I need custom CI/CD logic?**  
A: Generated workflows are just YAML. Edit them freely. Or use `--template custom.yml` to use your own.

**Q: Does this work with monorepos?**  
A: Yes. cicd-auto detects multi-workspace projects and generates per-workspace workflows.

**Q: Can I use this with existing CI/CD?**  
A: Yes. It can read existing workflows and suggest improvements.

**Q: How do I contribute?**  
A: See [CONTRIBUTING.md](CONTRIBUTING.md). We welcome language detectors, platform templates, and bug reports.

---

## License

MIT — Use freely, commercially or not.

---

## Community

- **GitHub Issues**: [Report bugs](https://github.com/btotharye/cicd-auto/issues)
- **Discussions**: [Ask questions](https://github.com/btotharye/cicd-auto/discussions)
- **Contributing**: [See CONTRIBUTING.md](CONTRIBUTING.md)

---

Built with ❤️ for developers who have better things to do than write YAML.
