import os

# The bundled database. The file name carries the package version whose factors it holds; change it here only.
DATABASE_FILE = "landcover_lca_database_0.3.0.db"


def get_local_dir():
    """Gets the directory containing this script

    Returns:
        str: full path to the the script's directory
    """
    return os.path.dirname(os.path.realpath(__file__))


def get_database_path():
    """Full path to the bundled SQLite database (``DATABASE_FILE`` in this directory)."""
    return os.path.join(get_local_dir(), DATABASE_FILE)
