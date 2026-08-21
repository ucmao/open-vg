# Contributing to VidGen 🎨⚡

First off, thank you for considering contributing to **VidGen**! It's open-source projects like this that make the developer community an amazing place to build, learn, and create.

## 📜 Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to the project maintainers.

## 🚀 How Can I Contribute?

### 1. Reporting Bugs
Before creating bug reports, please check existing issues as the problem might already be reported. When creating a bug report, please include:
- A clear, descriptive title.
- Steps to reproduce the issue.
- Expected vs actual behavior.
- Environment details (Node.js version, Python version, OS).

### 2. Suggesting Enhancements
Feature requests are tracked as GitHub issues. When creating an enhancement request, please specify:
- The problem you are trying to solve or the feature capability needed.
- Suggested implementation or design details.

### 3. Submitting Pull Requests (PRs)
1. **Fork the Repository**: Create your feature branch from `main`.
2. **Local Setup**: Follow the setup instructions in [README.md](../README.md).
3. **Commit Messages**: Write clear, descriptive commit messages.
4. **Code Quality**: Ensure code is formatted cleanly and adheres to repository conventions.
5. **Submit PR**: Open a Pull Request against the `main` branch with a thorough explanation of changes.

## 🛠️ Development Setup

### Backend (Python / FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Nuxt 3)
```bash
cd web
npm install
npm run dev
```

### Admin Panel (Nuxt 3)
```bash
cd admin
npm install
npm run dev
```

Thank you for contributing! ❤️
