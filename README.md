# nadamq

[![Build status](https://ci.appveyor.com/api/projects/status/rp9tnteiugbacc9v?svg=true)](https://ci.appveyor.com/project/SciBots/nadamq)

Low overhead packets with checksum validation.

API includes `nadamq.NadaMq.cPacket` type and `nadamq.NadaMq.cPacketParser`.

See [`nadamq/tests`](nadamq/tests) for example usage.


Build
=====

Install `conda-build`:

    conda install "conda-build>=3.4.2"

Build Python 3 packages:

    conda build .conda-recipe


Install
=======

Install the latest release from the [`sci-bots` Conda channel][sci-bots] using:

    conda install -c alexsk nadamq


[sci-bots]: https://anaconda.org/sci-bots
