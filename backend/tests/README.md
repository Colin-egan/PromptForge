# PromptForge Test Suite

This directory contains the test suite for the PromptForge backend.

## Test Structure

- `test_watsonx_client.py` - Unit tests for IBM watsonx.ai client wrapper
- `test_integration.py` - End-to-end integration tests for complete workflows
- `pytest.ini` - Pytest configuration (in parent directory)

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Or install all backend dependencies
pip install -r requirements.txt
```

### Run All Tests

```bash
# From backend directory
pytest

# With coverage report
pytest --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test Files

```bash
# Unit tests only
pytest tests/test_watsonx_client.py

# Integration tests only
pytest tests/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_integration.py::TestEndToEndWorkflows

# Run a specific test function
pytest tests/test_integration.py::TestEndToEndWorkflows::test_01_new_model_generation_workflow
```

### Run Tests with Markers

```bash
# Run only unit tests (when markers are added)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Verbose Output

```bash
# Show detailed output
pytest -v

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

## Test Coverage

The test suite covers:

### End-to-End Workflows (test_integration.py)
1. **New Model Generation** - Complete flow from description to rendered model
2. **Conversational Editing** - Editing existing models with natural language
3. **Parameter Adjustment** - Updating model parameters via sliders
4. **Print-Readiness Analysis** - Analyzing models for 3D printing issues
5. **Export Functionality** - Downloading models in various formats

### Error Handling
- Invalid model IDs
- Empty descriptions
- Malformed requests
- Code execution failures
- API failures

### Concurrency
- Multiple simultaneous model generations
- Thread safety verification

### Unit Tests (test_watsonx_client.py)
- Configuration validation
- Text generation with retry logic
- Embedding generation
- Prompt formatting
- Health checks
- Singleton pattern

## Mocking Strategy

Tests use mocking to avoid:
- Real watsonx.ai API calls (expensive and slow)
- Docker container execution (requires Docker daemon)
- ChromaDB operations (requires database setup)

Mocks are configured in fixtures:
- `mock_watsonx` - Mocks IBM watsonx.ai client
- `mock_sandbox` - Mocks Docker sandbox manager
- `mock_chroma` - Mocks ChromaDB client

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use descriptive names that explain what is being tested

### Test Structure
```python
def test_feature_name(client, mock_watsonx, mock_sandbox):
    """
    Test description explaining:
    - What is being tested
    - Expected behavior
    - Edge cases covered
    """
    # Arrange - Set up test data
    test_data = {...}
    
    # Act - Execute the code being tested
    response = client.post("/api/endpoint", json=test_data)
    
    # Assert - Verify the results
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Adding Markers
```python
@pytest.mark.integration
@pytest.mark.slow
def test_complex_workflow(client):
    """Test that takes a long time."""
    pass
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- No external dependencies required (all mocked)
- Fast execution (< 1 minute for full suite)
- Clear failure messages
- Exit codes for automation

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Troubleshooting

### Import Errors
If you see import errors, ensure you're running pytest from the `backend` directory:
```bash
cd backend
pytest
```

### Mock Not Working
Verify the import path in the patch decorator matches the actual import in the code:
```python
# If code uses: from app.main import watsonx_client
# Then patch: @patch('app.main.watsonx_client')
```

### Async Tests Failing
Ensure pytest-asyncio is installed and asyncio_mode is set in pytest.ini:
```ini
asyncio_mode = auto
```

## Test Metrics

Target metrics:
- **Coverage**: > 80% code coverage
- **Speed**: < 1 minute for full suite
- **Reliability**: 0 flaky tests
- **Maintainability**: Clear, documented tests

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass before committing
3. Add integration tests for user-facing features
4. Update this README if adding new test categories