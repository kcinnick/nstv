# Tests Directory

This directory contains project-level tests and debugging scripts organized by purpose.

## Structure

```
tests/
├── debug/          # Debug and exploration scripts
├── integration/    # Integration tests (cross-module testing)
└── unit/           # Unit tests (future - isolated component tests)
```

## Directory Purpose

### `debug/`
One-off scripts used for debugging, exploring APIs, or troubleshooting specific issues.
These are not formal tests but useful for development and issue investigation.

**Files**:
- `debug_movie_search.py` - Movie search API testing
- `debug_tvdb_search.py` - TVDB API exploration

**Usage**: Run directly with Python when needed for debugging.

### `integration/`
Integration tests that verify multiple components work together correctly.
These tests may interact with external services (Plex, TVDB) or the database.

**Files**:
- `test_duplicate_detection.py` - Tests for duplicate detection logic
- `test_movie_gid.py` - Movie GID functionality tests
- `test_tvdb_matching.py` - TVDB matching integration tests

**Usage**: Run with pytest from project root:
```bash
pytest tests/integration/
```

### `unit/`
Future location for isolated unit tests that don't require external dependencies.

**Usage**: Run with pytest from project root:
```bash
pytest tests/unit/
```

## Application-Level Tests

Note: Django app-specific tests are located in `nstv/tests/` directory:
- View tests (testIndex.py, testMovieIndex.py, etc.)
- Model tests (testEpisode.py, testCastMember.py, etc.)
- Feature tests (testAddMoviePage.py, testAddShowPage.py, etc.)

Run app tests with:
```bash
pytest nstv/tests/
```

## Running All Tests

To run all tests (both project-level and app-level):
```bash
pytest
```

To run with coverage:
```bash
pytest --cov=nstv --cov-report=html
```

## Test Organization Guidelines

- **Debug scripts**: Quick exploration and troubleshooting → `tests/debug/`
- **Integration tests**: Multi-component or external service tests → `tests/integration/`
- **Unit tests**: Isolated component tests → `tests/unit/`
- **Django app tests**: App-specific functionality → `nstv/tests/`
- **Management command tests**: Django commands → `nstv/tests/` (e.g., testAuditEpisodeDuplicatesCommand.py)

## Adding New Tests

1. Determine test type (debug, integration, unit, or app-specific)
2. Place in appropriate directory
3. Follow naming convention: `test_*.py` or `debug_*.py`
4. Add docstrings explaining what the test validates
5. Update this README if adding new categories
