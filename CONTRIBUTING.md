# Contributing to claude-code-vector-memory

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/claude-code-vector-memory.git
   cd claude-code-vector-memory
   ```
3. **Set up the development environment**:
   ```bash
   ./setup.sh  # On Linux/macOS
   setup.bat   # On Windows
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:
   ```bash
   ./scripts/run_tests.sh
   python scripts/health_check.py
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "Add semantic search performance optimization"
   ```

### Coding Standards

- **Python Style**: Follow PEP 8 guidelines
- **Docstrings**: Use Google-style docstrings for functions and classes
- **Type Hints**: Include type hints for function parameters and returns
- **Error Handling**: Use appropriate exception handling with informative messages

### Testing

- **Unit Tests**: Add tests for new functionality in the `tests/` directory
- **Integration Tests**: Ensure changes work with the full system
- **Health Checks**: Verify system diagnostics still pass

Example test structure:
```python
def test_new_feature():
    """Test description of what this validates."""
    # Test implementation
    assert expected_result == actual_result
```

### Documentation

- **Update README.md** if adding new features or changing usage
- **Add docstrings** to new functions and classes
- **Update CHANGELOG.md** with your changes

## Areas for Contribution

### High Priority
- **Performance optimizations** for large summary collections
- **Additional embedding models** support
- **Search result filtering** by date, project, or technology
- **Export/import** functionality for databases

### Medium Priority
- **Search result ranking** improvements
- **Metadata extraction** enhancements
- **Error handling** improvements
- **Documentation** and examples

### Low Priority
- **UI improvements** for terminal output
- **Additional file formats** support beyond markdown
- **Search history** and saved queries

## Submitting Changes

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference to any related issues

3. **Ensure CI passes** (when GitHub Actions are added)

4. **Respond to feedback** during code review

## Bug Reports

When reporting bugs, please include:
- **Environment details**: OS, Python version, Claude Code version
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error messages or logs**
- **Health check output** if relevant

## Feature Requests

For feature requests, please:
- **Describe the use case** and problem being solved
- **Propose a solution** or approach
- **Consider backwards compatibility**
- **Discuss performance implications**

## Code Review Process

All changes require review before merging:
- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Testing**: Are there appropriate tests?
- **Documentation**: Is documentation updated?
- **Performance**: Does it maintain or improve performance?

## Questions?

Feel free to open an issue for questions about:
- **Contributing process**
- **Technical implementation details**
- **Feature discussions**
- **Development environment setup**

Thank you for contributing to making Claude Code more powerful with persistent memory!