import sys
import os

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
sys.path.append(os.path.abspath('..'))


extensions = ['sphinx.ext.autodoc']

project = 'ImageIQ'
copyright = f'2024, Olga Sirenko, AndriyBatig1992, Sonia Dudiy, Vasyl Boliukh'
authors = ['AndriyBatig1992 <ashabatig1992@gmail.com>', 'Olga Sirenko <olga19022020@gmail.com>', 'Sonia Dudiy <sonia09012004@gmail.com>', 'Vasyl Boliukh <vskesha@gmail.com>']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']

