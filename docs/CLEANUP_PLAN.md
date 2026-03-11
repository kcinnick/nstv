# Codebase Cleanup Plan
**Date**: March 10, 2026  
**Branch**: feature/codebase-cleanup  
**Status**: Planning Phase

## Current Structure Analysis

### Root Directory Issues

#### Files That Should Be Moved
```
Root directory (C:\Users\Nick\nstv\)
├── debug_movie_search.py          → Move to tests/ or scripts/debug/
├── debug_tvdb_search.py           → Move to tests/ or scripts/debug/
├── test_duplicate_detection.py    → Move to tests/ or nstv/tests/
├── test_movie_gid.py              → Move to tests/ or nstv/tests/
├── test_tvdb_matching.py          → Move to tests/ or nstv/tests/
└── frontend-design-guidelines.md  → Move to docs/
```

#### Duplicate Virtual Environments
```
├── .venv/      (Active - 15,000+ files)
├── venv/       (Unused? - Should verify)
└── activate/   (Unclear purpose - possibly old venv?)
```

**Action**: Keep only `.venv/`, remove duplicates after verification

### Directory Structure Overview

```
nstv/                           # Project root
├── .venv/                      # ✓ Virtual environment (active)
├── activate/                   # ⚠ Investigate - old venv?
├── venv/                       # ⚠ Duplicate venv?
├── djangoProject/              # ✓ Django settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── nstv/                       # ✓ Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── tables.py
│   ├── download.py
│   ├── migrations/             # ✓ Database migrations
│   ├── management/             # ✓ Django commands
│   │   └── commands/
│   │       ├── audit_episode_duplicates.py
│   │       ├── enrich_from_tvdb.py
│   │       ├── fix_movie_titles.py
│   │       └── process_downloads.py
│   ├── tests/                  # ✓ Application tests
│   │   ├── testAddMoviePage.py
│   │   ├── testAddShowPage.py
│   │   ├── testAuditEpisodeDuplicatesCommand.py
│   │   ├── testCastMember.py
│   │   ├── testDelete.py
│   │   ├── testDownload.py
│   │   ├── testEpisode.py
│   │   ├── testIndex.py
│   │   ├── testMovieIndex.py
│   │   ├── testPlexController.py
│   │   ├── testShowIndex.py
│   │   └── testTvdbImportDedup.py
│   ├── plexController/         # ✓ Plex integration
│   │   ├── add_episodes_to_show.py
│   │   ├── add_movies_to_nstv.py
│   │   ├── add_shows_to_nstv.py
│   │   ├── duplicate_deletion.py
│   │   ├── find_duplicates.py
│   │   ├── plexDance.py
│   │   └── quality_analyzer.py
│   ├── get_info_from_tvdb/     # ✓ TVDB integration
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── get_actors_for_series.py
│   ├── kissasian/              # ⚠ Unused? Verify if still needed
│   │   └── download.py
│   └── utils/                  # ⚠ Only 1 file, consider reorganizing
│       └── rename_running_man_episodes.py
├── templates/                  # ✓ Django templates
│   ├── base.html
│   ├── add_movie.html
│   ├── add_show.html
│   ├── cast_member.html
│   ├── index.html
│   ├── missing_episodes.html
│   ├── movie.html
│   ├── movies_index.html
│   ├── search.html
│   ├── show.html
│   └── shows_index.html
├── scripts/                    # ✓ Automation scripts
│   ├── nzbget_postprocess.py
│   ├── preflight_check.py
│   ├── run_download_processor.bat
│   ├── run_download_processor.ps1
│   └── README.md
├── docs/                       # ✓ Documentation
│   ├── BUGS.md
│   ├── CODE_AUDIT.md
│   ├── DEPLOYMENT.md
│   ├── MANUAL_TASKS.md
│   ├── POST_DOWNLOAD_AUTOMATION.md
│   └── README.md
├── logs/                       # ✓ Log files
└── .pytest_cache/              # ⚠ Can be gitignored

Root-level files to organize:
├── debug_movie_search.py       # ⚠ Move to tests/debug/
├── debug_tvdb_search.py        # ⚠ Move to tests/debug/
├── test_duplicate_detection.py # ⚠ Move to tests/integration/
├── test_movie_gid.py           # ⚠ Move to tests/integration/
├── test_tvdb_matching.py       # ⚠ Move to tests/integration/
├── frontend-design-guidelines.md # ⚠ Move to docs/
├── manage.py                   # ✓ Keep (Django entry point)
├── pytest.ini                  # ✓ Keep (pytest config)
├── requirements.txt            # ✓ Keep (dependencies)
├── README.rst                  # ✓ Keep (primary readme)
├── instructions.md             # ✓ Keep (AI instructions)
├── .env.example                # ✓ Keep (env template)
└── .gitignore                  # ✓ Keep (git config)
```

## Cleanup Tasks - Phase 1: Structure

### Priority 1: Organize Root Directory (High Impact, Low Risk)

#### Task 1.1: Create Proper Test Structure
```bash
mkdir tests/
mkdir tests/debug/
mkdir tests/integration/
mkdir tests/unit/
```

**Move files**:
- `debug_movie_search.py` → `tests/debug/`
- `debug_tvdb_search.py` → `tests/debug/`
- `test_duplicate_detection.py` → `tests/integration/`
- `test_movie_gid.py` → `tests/integration/`
- `test_tvdb_matching.py` → `tests/integration/`

**Benefits**:
- Clean root directory
- Clear separation of test types
- Easier to run specific test categories

#### Task 1.2: Organize Documentation
```bash
Move: frontend-design-guidelines.md → docs/FRONTEND_GUIDELINES.md
```

**Benefits**:
- All documentation in one place
- Consistent naming (uppercase .md files in docs/)

#### Task 1.3: Clean Up Virtual Environments
```bash
# Investigate and remove duplicates
- Verify .venv/ is active (contains installed packages)
- Check if venv/ is used (probably old)
- Check if activate/ is old virtual env
- Remove unused virtual environments
- Update .gitignore to ensure all venvs ignored
```

**Benefits**:
- Reduce directory clutter
- Avoid confusion about which venv to use
- Save disk space

### Priority 2: Application Structure Review (Medium Impact, Low Risk)

#### Task 2.1: Review kissasian/ Module
**Question**: Is this still used?
- Check if download.py is imported anywhere
- Check git history for last usage
- **Options**:
  - Delete if unused
  - Document if deprecated but kept for reference
  - Move to scripts/ if it's a utility

#### Task 2.2: Consolidate Utils
**Current**: `nstv/utils/` has only 1 file
- Check if `rename_running_man_episodes.py` is still used
- **Options**:
  - Move to scripts/ if it's a one-off tool
  - Keep utils/ if planning to add more utilities
  - Move to plexController/ if it's Plex-related

#### Task 2.3: Review __pycache__ and Build Artifacts
```bash
# Ensure gitignore covers:
- __pycache__/
- *.pyc
- .pytest_cache/
- *.log
- .env (but not .env.example)
```

### Priority 3: .gitignore Enhancement (High Value, Zero Risk)

#### Current Issues
- Need to verify .gitignore covers all the right patterns

#### Proposed Additions
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environments
venv/
.venv/
ENV/
env/
activate/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
*.cover

# Django
*.log
db.sqlite3
db.sqlite3-journal
/staticfiles/
/mediafiles/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env

# Logs
logs/*.log
```

## Proposed Folder Structure (After Cleanup)

```
nstv/                           # Project root
├── .venv/                      # Virtual environment (gitignored)
├── djangoProject/              # Django settings
├── nstv/                       # Main application
│   ├── management/
│   │   └── commands/           # Django management commands
│   ├── migrations/             # Database migrations
│   ├── plexController/         # Plex integration modules
│   ├── get_info_from_tvdb/     # TVDB integration modules
│   └── tests/                  # Unit tests for app
├── templates/                  # Django HTML templates
├── scripts/                    # Automation & utility scripts
│   ├── nzbget_postprocess.py
│   ├── preflight_check.py
│   ├── run_download_processor.bat
│   └── run_download_processor.ps1
├── tests/                      # Project-level tests
│   ├── debug/                  # Debug/exploration scripts
│   │   ├── debug_movie_search.py
│   │   └── debug_tvdb_search.py
│   ├── integration/            # Integration tests
│   │   ├── test_duplicate_detection.py
│   │   ├── test_movie_gid.py
│   │   └── test_tvdb_matching.py
│   └── unit/                   # Unit tests (future)
├── docs/                       # All documentation
│   ├── README.md
│   ├── BUGS.md
│   ├── CODE_AUDIT.md
│   ├── DEPLOYMENT.md
│   ├── FRONTEND_GUIDELINES.md
│   ├── MANUAL_TASKS.md
│   └── POST_DOWNLOAD_AUTOMATION.md
├── logs/                       # Application logs (gitignored)
├── manage.py                   # Django entry point
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── README.rst                  # Primary readme
├── instructions.md             # AI agent instructions
├── .env.example                # Environment template
└── .gitignore                  # Git ignore rules
```

## Implementation Plan

### Phase 1: Structural Cleanup (This Branch)
1. ✅ Create cleanup branch
2. ⏳ Enhance .gitignore
3. ⏳ Create tests/ directory structure
4. ⏳ Move test files to appropriate locations
5. ⏳ Move frontend-design-guidelines.md to docs/
6. ⏳ Verify and document kissasian/ and utils/ status
7. ⏳ Identify and remove duplicate virtual environments
8. ⏳ Update any import statements if paths change
9. ⏳ Run tests to verify nothing broke
10. ⏳ Commit with detailed changelog

### Phase 2: Code Quality Branches (Future)
After structural cleanup, create separate branches for:
- **feature/remove-unused-code**: Remove dead code, unused imports
- **feature/improve-naming**: Rename poorly named variables/functions
- **feature/add-docstrings**: Document modules, classes, functions
- **feature/type-hints**: Add type annotations
- **feature/refactor-views**: Split large view functions
- **feature/refactor-models**: Review model structure
- **feature/test-coverage**: Increase test coverage
- **feature/linting**: Add black, flake8, mypy configs

### Phase 3: Documentation Branches (Future)
- **feature/api-docs**: Document internal APIs
- **feature/setup-guide**: Comprehensive setup instructions
- **feature/architecture-docs**: System architecture documentation

## Success Criteria

### Phase 1 Complete When:
- [x] All root-level test files moved to tests/
- [ ] All documentation in docs/
- [ ] Only one active virtual environment
- [ ] .gitignore comprehensive and correct
- [ ] No broken imports
- [ ] All existing tests still pass
- [ ] Clean `git status` output

### Overall Success:
- New contributors can understand project structure quickly
- Easy to find any file based on its purpose
- No confusion about which files are active vs. historical
- Clear separation of concerns (tests, docs, code, scripts)

## Notes

- Keep commits small and focused
- Test after each structural change
- Document any surprising discoveries
- Don't delete anything without verifying it's unused
- Keep this plan updated as we work
