# GitHub Action: cicd-auto

Auto-generate CI/CD workflows for your GitHub repository in one click.

## Quick Start

Add to your workflow file (`.github/workflows/setup.yml`):

```yaml
name: Auto CI/CD Setup
on: workflow_dispatch

jobs:
  setup:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: btotharye/cicd-auto@v1
        with:
          platforms: 'github'
          create-pr: true
```

Then:
1. Go to **Actions** tab
2. Select "Auto CI/CD Setup"
3. Click "Run workflow"
4. A pull request will be created with generated workflows

## Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `platforms` | Target platforms: `github`, `gitlab`, `jenkins`, `buildkite`, `circleci` | `github` | No |
| `create-pr` | Create a pull request with changes | `true` | No |
| `branch-name` | Branch name for pull request | `feat/auto-cicd` | No |
| `commit-message` | Commit message | `ci: auto-generate CI/CD workflows` | No |
| `pr-title` | Pull request title | `ci: auto-generate CI/CD workflows` | No |
| `pr-body` | Pull request body | `Auto-generated CI/CD configuration via cicd-auto` | No |
| `python-version` | Python version for runner | `3.11` | No |

## Outputs

| Output | Description |
|--------|-------------|
| `generated-files` | Comma-separated list of generated files |
| `pr-url` | URL of created pull request (if created) |
| `pr-number` | Number of created pull request (if created) |

## Examples

### Generate for GitHub Only

```yaml
- uses: btotharye/cicd-auto@v1
  with:
    platforms: 'github'
    create-pr: true
```

### Generate for Multiple Platforms

```yaml
- uses: btotharye/cicd-auto@v1
  with:
    platforms: 'github,gitlab,jenkins'
    create-pr: true
```

### Custom Branch & PR Title

```yaml
- uses: btotharye/cicd-auto@v1
  with:
    platforms: 'github'
    create-pr: true
    branch-name: 'ci/setup-workflows'
    pr-title: 'chore(ci): setup GitHub Actions workflows'
    pr-body: 'Auto-generated via cicd-auto. Please review and merge.'
```

### Run on Schedule

```yaml
name: Weekly CI/CD Audit
on:
  schedule:
    - cron: '0 9 * * MON'

jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: btotharye/cicd-auto@v1
        with:
          platforms: 'github'
          create-pr: true
          pr-title: 'ci: weekly CI/CD audit & update'
```

### Manual with Inputs

```yaml
name: Generate CI/CD
on:
  workflow_dispatch:
    inputs:
      platforms:
        description: 'Platforms'
        required: true
        default: 'github'
        type: choice
        options:
          - github
          - gitlab
          - jenkins
          - buildkite
          - 'github,gitlab'

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: btotharye/cicd-auto@v1
        with:
          platforms: ${{ inputs.platforms }}
          create-pr: true
```

## What Gets Generated

### GitHub Actions
- `.github/workflows/ci.yml` — Testing, linting, security scanning
- `.github/workflows/cd.yml` — Docker builds, releases, deployments
- `.github/dependabot.yml` — Automated dependency updates
- `.pre-commit-config.yaml` — Pre-commit hooks for local development

### GitLab CI
- `.gitlab-ci.yml` — Full pipeline with stages

### Jenkins
- `Jenkinsfile` — Declarative pipeline

### Buildkite
- `.buildkite/pipeline.yml` — Pipeline configuration

## How It Works

1. **Analyzes** your repository to detect:
   - Language (Python, Node.js, Go, Rust, etc.)
   - Framework (FastAPI, Django, Express, etc.)
   - Package manager (uv, poetry, npm, cargo, etc.)
   - Test framework (pytest, jest, go test, etc.)

2. **Generates** production-ready workflows for your stack

3. **Creates PR** with all changes (if `create-pr: true`)

4. **Includes** best practices:
   - Matrix testing across versions
   - Caching for faster runs
   - Security scanning
   - Coverage reporting
   - Pre-commit hooks
   - Dependency updates

## Permissions

The action requires these GitHub permissions:

```yaml
permissions:
  contents: write        # To commit changes
  pull-requests: write   # To create pull requests
```

## Features

✅ **Multi-language** — Python, Node.js, Go, Rust, Java, C#, Ruby, PHP  
✅ **Multi-platform** — GitHub, GitLab, Jenkins, Buildkite, CircleCI  
✅ **Smart detection** — Auto-detects your project type  
✅ **Best practices** — Production-grade configurations  
✅ **Extensible** — Easy to customize after generation  
✅ **No config needed** — Works out of the box  

## FAQ

**Q: Can I edit the generated workflows?**  
A: Yes! Generated workflows are just YAML. Edit freely.

**Q: Will it overwrite existing workflows?**  
A: No. If workflows exist, they won't be overwritten. Review in the PR.

**Q: What if I don't want to use some platforms?**  
A: Set `platforms: 'github'` (or just the ones you want).

**Q: Can I run this periodically?**  
A: Yes, use `schedule` trigger to run weekly/monthly audits.

**Q: How do I use this in other repositories?**  
A: Create `.github/workflows/setup.yml` with the action config and run.

## Troubleshooting

### Action fails to detect project type
- Ensure you're using standard project structures
- Add `pyproject.toml`, `package.json`, `go.mod`, etc. as needed

### PR not created
- Check permissions: need `contents: write` and `pull-requests: write`
- Verify `create-pr: true` in workflow input

### Generated workflows don't match my needs
- Edit them in the PR before merging
- Open an issue on GitHub for feature requests

## Contributing

Have ideas for improvements?

- [Open an issue](https://github.com/btotharye/cicd-auto/issues)
- [Start a discussion](https://github.com/btotharye/cicd-auto/discussions)
- [Create a pull request](https://github.com/btotharye/cicd-auto/pulls)

## License

MIT — Use freely!

---

**For more info:** [cicd-auto GitHub Repository](https://github.com/btotharye/cicd-auto)
