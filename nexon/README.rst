.. image:: https://raw.githubusercontent.com/mahirox36/nexon/master/assets/repo-banner.svg
   :alt: Nextcord

.. image:: https://img.shields.io/discord/1262297191884521514?color=blue&label=discord
   :target: https://discord.gg/HC2bryKU5Y
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/nexon.svg
   :target: https://pypi.org/project/nexon/
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/dm/nexon?color=informational&label=pypi%20downloads
   :target: https://pypi.org/project/nexon/
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/nextcord.svg
   :target: https://pypi.org/project/nexon/
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/readthedocs/nextcord
   :target: https://docs.nextcord.dev/
   :alt: Nextcord documentation

Nexon
--------

This is a custom fork of Nextcord, designed to extend its features with additional utilities and enhancements while maintaining compatibility with the original API.

Key Features of Nexon
------------------------
* **Optimized Performance**: A fast, cached data collection and management system for users and guilds.
* **Achievement Badges**: Automatically adds achievement badges to users.
* **Pre-configured Colour**: Colour schemes are synced across info, warning, and error messages for consistency.
* **Advanced Logging**: Enhanced logging for better debugging and monitoring.
* **Core Class Enhancements**: Expanded utilities for User, Member, Guild, and more.



Nextcord
----------
A modern, easy-to-use, feature-rich, and async-ready API wrapper for Discord written in Python.


Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``
- Proper rate limit handling
- Optimised in both speed and memory

Installing
----------

**Python 3.12 or higher is required**

To install the library without full voice support, you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U nexon

    # Windows
    py -3 -m pip install -U nexon

Otherwise to get voice support you should run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "nexon[voice]"

    # Windows
    py -3 -m pip install -U nexon[voice]

To install additional packages for speedup, run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "nexon[speed]"

    # Windows
    py -3 -m pip install -U nexon[speed]


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/mahirox36/nexon/
    $ cd nexon
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)
* `aiodns <https://pypi.org/project/aiodns/>`__, `Brotli <https://pypi.org/project/Brotli/>`__, `cchardet <https://pypi.org/project/cchardet/>`__ (for aiohttp speedup)
* `orjson <https://pypi.org/project/orjson/>`__ (for json speedup)

Please note that on Linux installing voice you must install the following packages via your favourite package manager (e.g. ``apt``, ``dnf``, etc) before running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.12-dev`` for Python 3.12)


Quick Example
~~~~~~~~~~~~~

.. code:: py

    import nexon
    from nexon.ext import commands


    bot = commands.Bot()

    @bot.slash_command(description="Replies with pong!")
    async def ping(interaction: nexon.Interaction):
        await interaction.send("Pong!", ephemeral=True)

    bot.run("token")

You can find more examples in the `examples directory <https://github.com/mahirox36/nexon/blob/master/examples/>`_.

**NOTE:** It is not advised to leave your token directly in your code, as it allows anyone with it to access your bot. If you intend to make your code public you should `store it securely <https://github.com/mahirox36/nexon/blob/master/examples/secure_token_storage.py/>`_.

Links
------

- `Documentation <https://docs.nextcord.dev/>`_
- `Official Discord Server <https://discord.gg/HC2bryKU5Y>`_
- `Official Nextcord Discord Server <https://discord.gg/nextcord>`_
- `Discord Developers Server <https://discord.gg/discord-developers>`_
