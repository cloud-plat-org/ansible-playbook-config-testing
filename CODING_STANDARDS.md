# Coding Standards

This document defines coding and documentation standards for this project to ensure consistency and maintainability.

## General Principles

- **No emojis or non-ASCII characters** in any code or documentation
- **Clear, professional language** in all documentation
- **ASCII-only characters** for maximum compatibility
- **Consistent formatting** across all files

## Documentation Standards

### Text Formatting
- Use standard ASCII characters only
- Replace emojis with descriptive text:
  - SUCCESS instead of checkmarks
  - ERROR/FAILED instead of X marks
  - NOTE/INFO instead of info icons
  - WARNING instead of warning icons

### Status Indicators
```
GOOD: [OK], [SUCCESS], [COMPLETED], [READY]
ERROR: [ERROR], [FAILED], [MISSING], [PENDING]
INFO: [NOTE], [INFO], [WARNING]
```

### Lists and Bullets
- Use standard `-` or `*` for bullet points
- Use `1.`, `2.`, etc. for numbered lists
- Use `a.`, `b.`, etc. for sub-lists

### Headers and Sections
- Use standard markdown headers (#, ##, ###)
- Clear, descriptive section names
- No decorative characters or emojis

## Code Standards

### Python
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Include docstrings for all functions and classes
- No emoji in print statements or comments
- Use clear status messages: "SUCCESS", "ERROR", "WARNING"
- Always explicitly set `check=False` in `subprocess.run()` calls for security

### YAML/Ansible
- Use 2-space indentation
- Clear, descriptive task names
- No emojis in task names or descriptions
- Use `msg:` for debug output with plain text

### Shell Scripts
- Use clear, descriptive echo statements
- No emojis in output
- Standard status indicators: [OK], [ERROR], [INFO]

## Documentation Structure

### README Files
- Clear purpose statement
- Installation/setup instructions
- Usage examples
- Troubleshooting section

### Comments
- Explain WHY, not just WHAT
- Use full sentences
- No decorative characters

## File Organization

### Directory Structure
- `scripts/` - Automation scripts
- `docs/` - Documentation files
- Clear, descriptive filenames
- Consistent naming conventions

### Configuration Files
- Use YAML for configuration when possible
- Clear, self-documenting structure
- Include comments explaining purpose

## Examples

### GOOD Documentation Style
```markdown
## Installation

1. Install required packages
2. Configure SSH keys
3. Test connectivity

Status: [SUCCESS] - Configuration complete
```
```

### BAD Documentation Style
```markdown
## Installation

1. Install required packages ✅
2. Configure SSH keys 🔑
3. Test connectivity 🚀

Status: ✅ Configuration complete 🎉
```

### GOOD Code Style
```python
```python
def configure_ssh(hostname, port):
    """Configure SSH connection for specified host."""
    print(f"[INFO] Configuring SSH for {hostname}:{port}")
    if success:
        print("[SUCCESS] SSH configuration complete")
    else:
        print("[ERROR] SSH configuration failed")
```

### BAD Code Style
```python
def configure_ssh(hostname, port):
    """Configure SSH connection for specified host."""
    print(f"🔧 Configuring SSH for {hostname}:{port}")
    if success:
        print("✅ SSH configuration complete")
    else:
        print("❌ SSH configuration failed")
```

## Enforcement

All new code and documentation must follow these standards. When updating existing files, remove any emojis or non-ASCII characters encountered.

## Tools

Use these tools to maintain standards:
- `grep -r "[^\x00-\x7F]" .` - Find non-ASCII characters
- `pylint` - Python code quality checking (configured via `.pylintrc`)
- `ansible-lint` - Ansible playbook linting (configured via `.ansible-lint`)
- Spell checkers for documentation
- `yamllint` - YAML file linting (check workflow files)

## Version History

- v1.0 - Initial standards document
- Focus on emoji removal and ASCII-only content
