# Contributing to RunZero ⚡

Thank you for your interest in contributing to **RunZero**! We welcome contributions from developers of all skill levels.

---

## 🛠️ Development Setup

1. **Fork and Clone the repository**:
   ```bash
   git clone https://github.com/el-j/run-zero.git
   cd run-zero
   ```

2. **Initialize Environment**:
   ```bash
   make env
   ```
   Edit `.env` and set your GitHub Personal Access Token (`ACCESS_TOKEN`) and GitHub username (`OWNER`).

3. **Build Images**:
   ```bash
   make build
   ```

4. **Run Local Test**:
   ```bash
   make test
   ```

---

## 🧪 Testing Guidelines

Before submitting a Pull Request, please ensure:
- Python script syntax is valid: `python3 -m py_compile docker/autoscaler.py`
- Bash entrypoint scripts are valid: `bash -n docker/start.sh`
- Docker Compose configuration parses cleanly: `docker compose config`
- The `make help` command runs with no formatting issues.

---

## 🚀 Submitting a Pull Request

1. Create a feature branch (`git checkout -b feature/amazing-feature`).
2. Commit your changes with clear, descriptive commit messages.
3. Push to your branch (`git push origin feature/amazing-feature`).
4. Open a Pull Request on GitHub targeting the `main` branch.
5. Describe your changes clearly in the PR description template.

---

## 💬 Code Style & Conventions

- **Python**: Follow PEP 8 style guidelines.
- **Shell**: Use `set -e` in bash scripts and quote variables to handle whitespace safely.
- **Docker**: Keep images minimal and multi-arch compliant (`arm64` and `amd64`).

Thank you for making RunZero better!
