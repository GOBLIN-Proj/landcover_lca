# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Landcover_LCA"
copyright = "2023-2026, Colm Duffy"
author = "Colm Duffy"
import os
import tomllib

with open(os.path.join(os.path.dirname(__file__), "..", "pyproject.toml"), "rb") as _f:
    release = tomllib.load(_f)["tool"]["poetry"]["version"]  # one source for the version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "html", "requirements.txt", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autoapi_dirs = ["../src/landcover_lca"]  # location to parse for API reference
html_theme = "sphinx_rtd_theme"
html_static_path = []
nb_execution_mode = "off"

# Class docstrings list their attributes and methods; AutoAPI documents the members too. Render those docstring
# sections as fields/notes, not directives, so each object is described once.
napoleon_use_ivar = True
napoleon_custom_sections = [("Methods", "notes_style")]
