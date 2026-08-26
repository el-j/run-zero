# Contributing to RunZero ⚡

Thank you for your interest in contributing to **RunZero**! We follow a structured **Git-Flow** branching model and **Semantic Versioning (SemVer)** to ensure high stability and continuous delivery.

---

## 🌳 Branching Strategy & Git Workflow

We use a standard branching strategy to ensure that only tested, release-ready code lands on `main`:

```text
  main (Production Releases / SemVer Tags: v2.0.0)
   ▲
   │  (Release PR / Merge)
  develop (Active Integration & Staging)
   ▲             ▲
   │             │
feat/my-feature  fix/bug-fix
```

### 1. `main` (Production Branch)
- Protected branch containing stable, production-ready code.
- Merges to `main` automatically trigger `.github/workflows/release.yml` to generate the next **SemVer release tag** and publish the GitHub Release with changelogs.

### 2. `develop` (Integration Branch)
- Active integration branch for upcoming releases.
- All feature and fix PRs should target `develop`.

### 3. Topic Branches (`feat/*`, `fix/*`, `docs/*`)
- Create feature branches off `develop`:
  ```bash
  git checkout develop
  git pull origin develop
  git checkout -b feat/your-feature-name
  ```
- Use conventional commits format (`feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...`).

---

## 🛠️ Development & Quality Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:el-j/run-zero.git
   cd run-zero
   ```

2. **Initialize Environment**:
   ```bash
   make env
   ```

3. **Run Testing Suite (100% Quality Mandate)**:
   ```bash
   make test           # 68 local unit tests
   make test-suite     # Flake8 linter + Mypy type check + Pytest coverage
   make mutation-test  # Mutmut mutation testing
   ```

4. **Astro Website Development**:
   ```bash
   make website-dev    # Start local Astro dev server
   make website-build  # Build production static bundle and sync to docs/
   ```

---

## 🚀 Submitting a Pull Request

1. Push your branch to GitHub:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request targeting the **`develop`** branch.
3. Verify that all CI validation checks pass in GitHub Actions.
4. Once reviewed and merged into `develop`, changes will be rolled into the next release on `main`.

Thank you for making RunZero better!
