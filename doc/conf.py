# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(0, os.path.normpath(os.path.join(__file__, "../..", "src")))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "UA Parser"
copyright = "2024, UA Parser Project"
author = "UA Parser Project"

version = "1.0"
release = "1.0"

rst_epilog = """
.. |pyyaml| replace:: ``PyYaml``
.. |re2| replace:: ``google-re2``
.. |regex| replace:: ``regex``

.. _pyyaml: https://pyyaml.org
.. _re2: https://pypi.org/project/google-re2
.. _regex: https://pypi.org/project/ua-parser-rs
"""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

html_theme = "alabaster"

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
