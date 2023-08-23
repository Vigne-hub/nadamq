from __future__ import absolute_import
import sys
from pprint import pprint
try:
    from Cython.Build import cythonize
except ImportError:
    CYTHON_BUILD = False
else:
    CYTHON_BUILD = True

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, install_distutils_tasks
from distutils.extension import Extension
from distutils.dep_util import newer

# Add package directory to Python path. This enables the use of `nadamq`
# functions for discovering, e.g., the path to the Arduino firmware sketch
# source files.
sys.path.insert(0, path('.').abspath())
import nadamq
import versioneer

here = path('.').abspath()
include_dirs = [str(here.relpathto(p)) for p in nadamq.get_includes()]
sources = [str(here.relpathto(p)) for p in nadamq.get_sources()]
sys.path += include_dirs

if CYTHON_BUILD:
    # Add the following to `extra_compile_args` to debug packet parser:
    #
    #     '-DVERBOSE_STATES'
    cy_config = dict(include_dirs=include_dirs, language='c++',
                     extra_compile_args=['-O3'])

    cy_exts = [Extension('nadamq.%s' % v, sources + ['nadamq/%s.pyx' % v],
                         **cy_config) for v in ('NadaMq', )]
    extensions = cythonize(cy_exts)
else:
    ext_config = dict(include_dirs=include_dirs,
                      extra_compile_args=['-O3'])
    extensions = [Extension('nadamq.%s' % v, sources + ['nadamq/%s.cpp' % v], **ext_config) for v in ('NadaMq', )]
pprint(extensions)

setup(name='nadamq',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Embedded-friendly transport layer, inspired by ZeroMQ',
      keywords='cython embedded zeromq transport packet parse',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/wheeler-microfluidics/nadamq',
      license='GPL',
      packages=['nadamq', ],
      # Install data listed in `MANIFEST.in`
      include_package_data=True,
      ext_modules=extensions)


@task
def build_arduino_library():
    import os
    import tarfile

    arduino_lib_dir = path('nadamq').joinpath('lib')
    if not arduino_lib_dir.isdir():
        arduino_lib_dir.mkdir()
    tf = tarfile.TarFile.bz2open(arduino_lib_dir
                                 .joinpath('NadaMQ-Arduino.tar.gz'), 'w')
    for s in nadamq.get_arduino_library_sources():
        tf.add(s, os.path.join('NadaMQ', os.path.basename(s)))
    tf.close()


@task
def build_packet_actions():
    sh('scons')


@task
def clean_packet_actions():
    sh('scons -c')


@task
@needs(['build_packet_actions'])
def copy_packet_actions():
    path('build/packet_actions.cpp').copy('nadamq/src')


@task
@needs(['copy_packet_actions', 'generate_setup', 'minilib',
        'setuptools.command.build'])
def build():
    pass


@task
@needs(['copy_packet_actions', 'generate_setup', 'minilib',
        'setuptools.command.build_ext'])
def build_ext():
    pass


@task
@needs('copy_packet_actions', 'generate_setup', 'minilib', 'build_ext',
       'build_arduino_library', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


NADAMQ_HEADERS = 'NadaMQ.h output_buffer.h packet_handler.h'.split(' ')
PACKET_HEADERS = 'BufferAllocator.h Packet.h PacketAllocator.h PacketHandler.h PacketParser.h PacketSocket.h PacketSocketEvents.h PacketStream.h PacketWriter.h SimpleCommand.h StreamPacketParser.h crc-16.cpp crc-16.h crc_common.cpp crc_common.h packet_actions.cpp'.split(' ')

import os
import shutil
import platformio_helpers as pioh
import path_helpers as ph
src_dir = ph.path('{{ SRC_DIR }}').joinpath('{{ MODULE_NAME }}', 'src')
install_dir = pioh.conda_arduino_include_path().joinpath('{{ LIB_NAME }}')
os.makedirs(install_dir, exist_ok=True)
for file_i in NADAMQ_HEADERS:
    src_file = src_dir.joinpath('Arduino', 'packet_handler', '{{ file_i }}')
    shutil.copy2(str(src_file), str(install_dir.joinpath(src_file.name)))

for file_i in PACKET_HEADERS:
    shutil.copy2(str(src_dir.joinpath('{{ file_i }}')), str(install_dir.joinpath('{{ file_i }}')))