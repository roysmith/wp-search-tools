A collection of tools for better searching of wikipedia.

# Directory layout

The code expects that the top-level directory will be named
wp_search_tools and will be visible from your $PYTHONPATH.  Note that
the git repo is named wp-search-tools, which implies that you need to
explicitly give it a different name when you clone it.  Example:

    cd $HOME/foo
    git clone git@github.com:roysmith/wp-search-tools.git wp_search_tools
    PYTHONPATH=$HOME/foo; export PYTHONPATH

The code depends on this layout, so it can do things like:

    from wp_search_tools import some_subpackage

# Virtual environment

It is strongly recommended that you set up a python venv dedicated to
this project.  If you're not setting up a new venv for every one of
your python projects, you're just doing it wrong.  Example:

    cd $HOME/foo
    python3 -m venv --prompt wp-search-tools venv
    pip install -r wp_search_tools/requirements.txt

It's not strictly required, but it's a good idea to get the latest
version of pip:

    pip install --upgrade pip
