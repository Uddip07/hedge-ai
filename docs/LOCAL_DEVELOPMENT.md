# Local Development Environment Setup

## Prerequisites
- Python 3.12+
- Git

---

## Step-by-Step Setup

```bash
# 1. Clone repository
git clone https://github.com/Uddip07/indian-hedge-fund-ai.git
cd indian-hedge-fund-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Run test suite
python -m unittest discover tests

# 5. Run static analysis
python -m mypy packages/ai/committee
python -m ruff check .
python -m black --check .
```
