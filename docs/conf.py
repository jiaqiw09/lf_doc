# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Project information -----------------------------------------------------
project = 'LlamaFactory'
copyright = '2024, LlamaFactory Team'
author = 'LlamaFactory Team'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
    'sphinx_rtd_theme',
    'sphinx_external_toc',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README.md'] # Exclude README.md if it is used as index

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_js_files = [
    'js/language_switcher.js',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# -- MyST configuration ------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

# -- External TOC configuration ----------------------------------------------
external_toc_path = "_toc.yml"  # Relative to source directory
external_toc_exclude_missing = False

# -- I18n configuration ------------------------------------------------------
# The language will be passed via command line -D language=...
locale_dirs = ['locale/']   # path is example but recommended.
gettext_compact = False     # optional.
