---
trigger: model_decision
---

# Python Testing Rules

- **Group tests into classes**: Organize related tests into class-based suites rather than standalone functions.
- **Suite Descriptions**: Test suite classes must have a docstring description explaining what the group of tests covers.
- **Test Function Docstrings**: Each test function must have a docstring describing:
  - The scenario being tested (minimum 1 sentence)
  - Assumptions (list of 1 or more assumptions about test scenario setup)
  - The pass/fail criteria (list of 1 or more criteria).
- **Fixtures**: Setup common state or dependencies using pytest fixtures, not helper functions or class methods.

### Test content:
- reach 100% test coverage
- features & requirements defined in specs or README must be verified with a test

### Example docstring

```
def test_db_session_lifecycle(self, db_session: Session):
   """
   A test requests `db_session`.

   Assumptions:
     - Test function using db_session fixture

   Criteria:
     - Session is provided.
     - Can interact with database (add/commit/refresh).
     - Data is visible within the test scope.
        
```