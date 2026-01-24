# Contributing to DTL Student Election

Thank you for your interest in contributing to the DTL Student Election project! We welcome contributions from the community.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

---

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to madhurrishis.is24@rvce.edu.in.

---

## How Can I Contribute?

### Reporting Bugs
- Check if the bug has already been reported in GitHub Issues.
- If not, create a new issue with:
  - A clear title and description
  - Steps to reproduce
  - Expected vs. actual behavior
  - Screenshots (if applicable)
  - Environment details (OS, Python version, browser)

### Suggesting Features
- Open a GitHub Issue with the "enhancement" label.
- Describe the feature and its use case clearly.
- Explain why this feature would be useful to most users.

### Code Contributions
- Fork the repository
- Create a feature branch (`git checkout -b feature/your-feature-name`)
- Make your changes
- Test thoroughly
- Submit a pull request

---

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dtl-student-election.git
   cd dtl-student-election
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your Firebase credentials and blockchain config

4. **Run locally**
   ```bash
   flask run
   ```

5. **Access the app**
   - Navigate to `http://localhost:5000`

---

## Pull Request Process

1. **Update documentation** if your changes affect user-facing features.
2. **Update PROJECT_OVERVIEW.md** for major architectural changes.
3. **Update CHANGELOG.md** under `[Unreleased]` section.
4. **Ensure your code follows** the style guidelines below.
5. **Test your changes** thoroughly before submitting.
6. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues (if any)
   - Screenshots/GIFs for UI changes

### PR Review Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] Documentation is updated
- [ ] No sensitive data (keys, credentials) in commits
- [ ] `.gitignore` is respected
- [ ] Changes are backward compatible (or migration path provided)

---

## Style Guidelines

### Python Code
- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings for non-trivial functions
- Keep functions focused and concise

### HTML/CSS
- Use semantic HTML5 tags
- Maintain consistent indentation (2 spaces)
- Keep CSS organized by component
- Ensure responsive design

### Git Commits
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs when relevant

---

## Questions?

Feel free to open a GitHub Discussion or reach out to the maintainers.

Thank you for contributing! 🎉
