# Installation

## Install from PyPI

**scholarpy** is available on [PyPI](https://pypi.org/project/scholarpy/). To install **scholarpy**, run this command in your terminal:

```bash
    pip install scholarpy
```

## Install from conda-forge

**scholarpy** is also available on [conda-forge](https://anaconda.org/conda-forge/scholarpy). If you have
[Anaconda](https://www.anaconda.com/distribution/#download-section) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your computer, you can install scholarpy using the following command:

```bash
    conda install scholarpy -c conda-forge
```

Optionally, you can install some [Jupyter notebook extensions](https://github.com/ipython-contrib/jupyter_contrib_nbextensions), which can improve your productivity in the notebook environment. Some useful extensions include Table of Contents, Gist-it, Autopep8, Variable Inspector, etc. See this [post](https://towardsdatascience.com/jupyter-notebook-extensions-517fa69d2231) for more information.

```bash
    conda install jupyter_contrib_nbextensions -c conda-forge
```

## Install from GitHub

To install the development version from GitHub using [Git](https://git-scm.com/), run the following command in your terminal:

```bash
    pip install git+https://github.com/giswqs/scholarpy
```

## Upgrade scholarpy

If you have installed **scholarpy** before and want to upgrade to the latest version, you can run the following command in your terminal:

```bash
    pip install -U scholarpy
```

If you use conda, you can update scholarpy to the latest version by running the following command in your terminal:

```bash
    conda update -c conda-forge scholarpy
```

To install the development version from GitHub directly within Jupyter notebook without using Git, run the following code:

```python
    import scholarpy
    scholarpy.update_package()
```
