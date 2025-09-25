# 🚀 Contributing to EasySwitch

Thank you for your interest in contributing to **EasySwitch**! This guide will help you contribute effectively while maintaining our quality standards.

## 📋 Table of Contents
- [Prerequisites](#-prerequisites)
- [Local Setup](#-local-setup)
- [Contribution Workflow](#-contribution-workflow)
- [Code Conventions](#-code-conventions)
- [Testing & Quality](#-testing--quality)
- [Issue Management](#-issue-management)
- [Code of Conduct](#-code-of-conduct)

---

## 🔍 Prerequisites
- Python 3.10+
- [UV](https://docs.astral.sh/uv/) (recommended) or pip
- Basic knowledge of payment APIs
- Familiarity with async testing

---

## 💻 Local Setup

### 1. Fork the Repository
Click "Fork" at the top-right of the [project's GitHub page](https://github.com/AllDotPy/easyswitch).

### 2. Clone the Project
```bash
git clone https://github.com/your-username/easyswitch.git
cd easyswitch
```

### 3. Set Up the Environment
**With UV (recommended):**
```bash
# Install UV
pip install uv

# Create virtual environment
uv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -e .[dev]
```

**With standard pip:**
```bash
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

---

## 🔄 Contribution Workflow

1. **Create a Branch**  
   ```bash
   git checkout -b feat/new-feature
   ```

2. **Implement Your Changes**  
   - Follow [code conventions](#-code-conventions)
   - Add relevant tests

3. **Verify Code Quality**  
   ```bash
   uv run lint   # Style check
   uv run test   # Run tests
   ```

4. **Push Changes**  
   ```bash
   git push origin feat/new-feature
   ```

5. **Open a Pull Request**  
   - Complete the PR template
   - Clearly describe your changes
   - Reference related issues

---

## ✨ Code Conventions

### General Structure
- **Typing**: Use type annotations everywhere
- **Async**: Prefer `async/await` for I/O operations
- **Exceptions**: Use the project's custom exceptions

### Style Guide
- **Naming**:
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
- **Docstrings**: Follow Google Style
  ```python
  def send_payment(amount: float) -> bool:
      """Sends payment to the aggregator.

      Args:
          amount: Amount to send (in XOF)

      Returns:
          bool: True if payment succeeded
      """
  ```

### Validation
- Use validators from `easyswitch.utils.validators`
- Always validate API inputs

---

## 🧪 Testing & Quality

### Running Tests
```bash
uv run test  # All tests
uv run test -k "test_payment"  # Specific tests
```

### Code Coverage
```bash
uv run coverage
```

### Best Practices
- 1 test per feature
- Isolated, idempotent tests
- Mock external APIs

---

## 🐛 Issue Management

### Reporting Bugs
1. Check for existing issues
2. Use the "Bug Report" template
3. Include:
   - Environment (Python, OS)
   - Reproduction steps
   - Relevant logs/errors

### Feature Proposals
1. Use the "Feature Request" template
2. Describe:
   - Use case
   - Expected impact
   - API sketch if applicable

---

## 🤝 Code of Conduct

We adhere to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating:
- Be kind and open-minded
- Accept constructive feedback
- Prioritize collaboration

---

## 🎉 First-Time Contributor?

Check out these labeled issues:
- `good first issue` for simple contributions
- `help wanted` for more challenging tasks

---

Thank you for helping make EasySwitch even better! 💪