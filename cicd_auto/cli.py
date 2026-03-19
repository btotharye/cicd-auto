"""Command-line interface for cicd-auto."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .analyzer import ProjectAnalyzer

console = Console()


@click.group()
def main():
    """Auto-generate production-ready CI/CD pipelines."""
    pass


@main.command()
@click.option("--repo", default=".", help="Repository path")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def analyze(repo: str, output_json: bool):
    """Analyze a repository and show detected stack."""
    try:
        import json as json_module
        
        analyzer = ProjectAnalyzer(repo)
        analysis = analyzer.analyze()
        
        if output_json:
            # Output as JSON
            output = {
                "language": analysis.language,
                "framework": analysis.framework,
                "package_manager": analysis.package_manager,
                "test_framework": analysis.test_framework,
                "platform": analysis.platform,
                "cloud": analysis.cloud,
                "has_dockerfile": analysis.has_dockerfile,
                "has_terraform": analysis.has_terraform,
                "has_k8s": analysis.has_k8s,
                "test_command": analysis.test_command,
                "lint_command": analysis.lint_command,
                "build_command": analysis.build_command,
                "python_version": analysis.python_version,
            }
            click.echo(json_module.dumps(output, indent=2))
            return
        
        # Pretty output
        console.print("\n[bold cyan]📊 Project Analysis[/bold cyan]\n")
        
        table = Table(title="Detected Stack", show_header=False, box=None)
        
        items = [
            ("Language", analysis.language or "Unknown"),
            ("Framework", analysis.framework or "Generic"),
            ("Package Manager", analysis.package_manager or "Unknown"),
            ("Test Framework", analysis.test_framework or "Unknown"),
            ("CI/CD Platform", analysis.platform or "GitHub Actions (default)"),
            ("Cloud Provider", analysis.cloud or "None detected"),
        ]
        
        if analysis.python_version:
            items.insert(2, ("Python Version", analysis.python_version))
        
        for key, value in items:
            color = "green" if value != "Unknown" and value != "None detected" else "yellow"
            table.add_row(f"[bold]{key}[/bold]", f"[{color}]{value}[/{color}]")
        
        console.print(table)
        
        # Build info
        console.print("\n[bold cyan]🔨 Build Info[/bold cyan]\n")
        
        build_info = [
            ("Has Dockerfile", "✓" if analysis.has_dockerfile else "✗"),
            ("Has Terraform", "✓" if analysis.has_terraform else "✗"),
            ("Has Kubernetes", "✓" if analysis.has_k8s else "✗"),
        ]
        
        for key, value in build_info:
            color = "green" if value == "✓" else "dim"
            console.print(f"  {key}: [{color}]{value}[/{color}]")
        
        # Commands
        if any([analysis.test_command, analysis.lint_command, analysis.build_command]):
            console.print("\n[bold cyan]🚀 Inferred Commands[/bold cyan]\n")
            
            if analysis.test_command:
                console.print(f"  Test:  [cyan]{analysis.test_command}[/cyan]")
            if analysis.lint_command:
                console.print(f"  Lint:  [cyan]{analysis.lint_command}[/cyan]")
            if analysis.build_command:
                console.print(f"  Build: [cyan]{analysis.build_command}[/cyan]")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error analyzing repository: {e}[/red]", file=sys.stderr)
        sys.exit(1)


@main.command()
@click.option("--repo", default=".", help="Repository path")
@click.option("--platform", "platforms", multiple=True, help="Target platforms (github, gitlab, jenkins, buildkite)")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without writing")
@click.option("--branch", default="feat/auto-cicd", help="Git branch for changes")
def generate(repo: str, platforms: tuple, dry_run: bool, branch: str):
    """Generate CI/CD workflows."""
    try:
        from .generator import DependabotGenerator, PreCommitGenerator, WorkflowGenerator
        
        analyzer = ProjectAnalyzer(repo)
        analysis = analyzer.analyze()
        
        if not analysis.language:
            console.print("[red]Could not detect project language[/red]", file=sys.stderr)
            sys.exit(1)
        
        # Default to detected platform or GitHub
        target_platforms = list(platforms) if platforms else [analysis.platform or "github"]
        
        console.print(f"\n[bold cyan]🚀 Generating CI/CD for {', '.join(target_platforms)}[/bold cyan]\n")
        
        console.print(f"  Language:        {analysis.language}")
        console.print(f"  Framework:       {analysis.framework or 'Generic'}")
        console.print(f"  Package Manager: {analysis.package_manager}")
        console.print(f"  Test Framework:  {analysis.test_framework}")
        console.print()
        
        # Generate workflows
        generator = WorkflowGenerator()
        precommit_gen = PreCommitGenerator()
        dependabot_gen = DependabotGenerator()
        
        all_workflows = {}
        
        for platform in target_platforms:
            if platform == "github":
                all_workflows.update(generator.generate_github_workflows(analysis))
            elif platform == "gitlab":
                all_workflows.update(generator.generate_gitlab_workflows(analysis))
            elif platform == "jenkins":
                all_workflows.update(generator.generate_jenkins_workflows(analysis))
            elif platform == "buildkite":
                all_workflows.update(generator.generate_buildkite_workflows(analysis))
        
        # Add pre-commit and dependabot (GitHub specific)
        if "github" in target_platforms:
            precommit_config = precommit_gen.generate_pre_commit_config(analysis)
            if precommit_config:
                all_workflows[".pre-commit-config.yaml"] = precommit_config
            
            dependabot_config = dependabot_gen.generate_dependabot_config(analysis)
            if dependabot_config:
                all_workflows[".github/dependabot.yml"] = dependabot_config
        
        if not all_workflows:
            console.print("[yellow]No workflows generated for detected configuration[/yellow]\n")
            return
        
        # Show summary
        console.print(f"[green]✓ Generated {len(all_workflows)} configuration files:[/green]\n")
        
        for filepath in sorted(all_workflows.keys()):
            console.print(f"  {filepath}")
        
        console.print()
        
        if dry_run:
            console.print("[bold cyan]Preview (--dry-run mode):[/bold cyan]\n")
            for filepath, content in sorted(all_workflows.items()):
                console.print(f"\n{'='*60}")
                console.print(f"File: [bold]{filepath}[/bold]")
                console.print(f"{'='*60}\n")
                
                # Show syntax highlighted content
                if filepath.endswith('.yml') or filepath.endswith('.yaml'):
                    syntax = Syntax(content, "yaml", theme="monokai", line_numbers=False)
                    console.print(syntax)
                elif filepath.endswith('.groovy'):
                    syntax = Syntax(content, "groovy", theme="monokai", line_numbers=False)
                    console.print(syntax)
                else:
                    console.print(content)
        else:
            # Write files
            repo_path = Path(repo)
            
            for filepath, content in all_workflows.items():
                full_path = repo_path / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            console.print(f"[green]✓ Files written to {repo}[/green]")
            console.print(f"\n[bold cyan]Next steps:[/bold cyan]")
            console.print(f"  1. Review the generated files")
            console.print(f"  2. Commit: git add {' '.join(all_workflows.keys())}")
            console.print(f"  3. Push: git push -u origin {branch}")
            console.print(f"  4. Create a pull request\n")
        
    except Exception as e:
        import traceback
        console.print(f"[red]Error generating workflows: {e}[/red]", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


@main.command()
@click.option("--repo", default=".", help="Repository path")
def init(repo: str):
    """Initialize ci/cd-auto in a repository."""
    try:
        repo_path = Path(repo)
        
        console.print("\n[bold cyan]🎯 Initializing cicd-auto[/bold cyan]\n")
        
        # Check if already initialized
        cicd_auto_dir = repo_path / ".cicd-auto"
        if cicd_auto_dir.exists():
            console.print(f"[yellow]Already initialized at {cicd_auto_dir}[/yellow]\n")
            return
        
        # Create config directory
        cicd_auto_dir.mkdir(exist_ok=True)
        
        # Create default config
        config = {
            "version": "1.0",
            "platforms": ["github"],
            "languages": ["python", "node", "go"],
        }
        
        config_file = cicd_auto_dir / "config.json"
        config_file.write_text(json.dumps(config, indent=2))
        
        console.print(f"✅ Initialized at {cicd_auto_dir}")
        console.print(f"   Config: {config_file}\n")
        
    except Exception as e:
        console.print(f"[red]Error initializing: {e}[/red]", file=sys.stderr)
        sys.exit(1)


@main.command()
def version():
    """Show version."""
    from . import __version__
    console.print(f"cicd-auto {__version__}")


if __name__ == "__main__":
    main()
