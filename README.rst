====
nstv
====

A Django-based application for managing and tracking TV shows and movies from your Plex server. Syncs metadata from Plex and TVDB, tracks episode availability, and provides a web interface for browsing your media library.

Features
--------

**Media Library Management**

* Sync TV shows, episodes, and movies from Plex server
* Import detailed metadata from TVDB (The Movie Database)
* Track which episodes are available on disk
* Anime detection via genre classification
* Cast member tracking

**Data Quality & Integrity**

* Automatic duplicate episode detection and cleanup
* Season number normalization (handles "S01", "Season 1", etc.)
* Title aliasing for shows with multiple names
* Three-tier episode matching (TVDB ID → season/episode → normalized title)

**User Interface**

* Browse shows and movies with poster art
* View episode lists and availability
* Search functionality
* Missing episode tracking
* Detailed cast information pages

Requirements
------------

* Python 3.12+
* PostgreSQL 16
* Plex Media Server
* TVDB API key

Quick Start
-----------

1. **Clone the repository**::

    git clone https://github.com/kcinnick/nstv.git
    cd nstv

2. **Create virtual environment**::

    python -m venv venv
    venv\Scripts\activate  # Windows
    source venv/bin/activate  # Linux/Mac

3. **Install dependencies**::

    pip install -r requirements.txt

4. **Configure environment variables**::

    cp .env.example .env
    # Edit .env with your credentials:
    # - DJANGO_DB_PASSWORD
    # - PLEX_EMAIL, PLEX_API_KEY, PLEX_SERVER
    # - TVDB_API_KEY

5. **Run migrations**::

    python manage.py migrate

6. **Create superuser**::

    python manage.py createsuperuser

7. **Sync from Plex**::

    python nstv/plexController/add_shows_to_nstv.py
    python nstv/plexController/add_movies_to_nstv.py

8. **Run development server**::

    python manage.py runserver

Management Commands
-------------------

**Audit Episode Duplicates**::

    # Check for duplicates (dry run)
    python manage.py audit_episode_duplicates
    
    # Fix duplicates by merging
    python manage.py audit_episode_duplicates --fix
    
    # Audit specific show
    python manage.py audit_episode_duplicates --show-id 123

Testing
-------

Run the test suite::

    pytest

Run specific test file::

    pytest nstv/tests/testAddShowPage.py

Check for Django issues::

    python manage.py check

Project Structure
-----------------

* ``nstv/`` - Main Django app
    * ``models.py`` - Database models (Show, Episode, Movie, CastMember)
    * ``views.py`` - Web interface views
    * ``plexController/`` - Plex sync scripts
    * ``get_info_from_tvdb/`` - TVDB metadata import
    * ``management/commands/`` - Django management commands
    * ``tests/`` - Test suite
* ``djangoProject/`` - Django project settings
* ``templates/`` - HTML templates
* ``docs/`` - Documentation and runbooks

Documentation
-------------

* ``instructions.md`` - Claude Sonnet 4.5 development guidelines
* ``docs/plex-rebuild-runbook.md`` - Step-by-step Plex sync instructions
* ``.env.example`` - Environment variable template

License
-------

MIT License
