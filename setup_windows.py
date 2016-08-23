import os, sys

# Note: if a matching gcc is available from the shell on Windows, its
#       probably safe to assume the user is in an MINGW or MSYS or Cygwin
#       environment, in which case he/she wants to compile with gcc for
#       Windows, in which case the correct compiler flags will be triggered
#       by is_mingw. This method is not great, improve it if you know a
#       better way to discriminate between compilers on Windows.
def ismingw():
    # currently this check detects mingw only on Windows. Extend for other
    # platforms if required:
    if (os.name != "nt"):
        return False

    # if the user defines DISTUTILS_USE_SDK or MSSdk, we expect they want
    # to use Microsoft's compiler (as described here:
    # https://github.com/cython/cython/wiki/CythonExtensionsOnWindows):
    if (os.getenv("DISTUTILS_USE_SDK") != None or os.getenv("MSSdk") != None):
        return False

    mingw32 = ""
    mingw64 = ""
    if (os.getenv("MINGW32_PREFIX")):
        mingw32 = os.getenv("MINGW32_PREFIX")
    if (os.getenv("MINGW64_PREFIX")):
        mingw64 = os.getenv("MINGW64_PREFIX")

    # if any invocation of gcc works, then we assume the user wants mingw:
    test = "gcc --version > NUL 2>&1"
    if (os.system(test) == 0 or os.system(mingw32+test) == 0 or os.system(mingw64+test) == 0):
        return True

    return False


def get_config():
    from setup_common import get_metadata_and_options, enabled, create_release_file

    metadata, options = get_metadata_and_options()

    is_mingw = ismingw()

    connector = options["connector"]

    extra_objects = []
    extra_compile_args = []

    if enabled(options, 'embedded'):
        client = "mysqld"
    else:
        if is_mingw:
            client = "mysql"
        else:
            client = "mysqlclient"

    library_dirs = [os.path.join(connector, r'lib/opt'), os.path.join(connector, r'lib')]
    libraries = [ client, 'kernel32', 'advapi32', 'wsock32' ]


    include_dirs = [ os.path.join(connector, r'include') ]
    if not is_mingw:
        extra_compile_args = [ '/Zl' ]

    name = "MySQL-python"
    if enabled(options, 'embedded'):
        name = name + "-embedded"
    metadata['name'] = name

    define_macros = [
        ('version_info', metadata['version_info']),
        ('__version__', metadata['version']),
        ]
    create_release_file(metadata)
    del metadata['version_info']
    ext_options = dict(
        name = "_mysql",
        library_dirs = library_dirs,
        libraries = libraries,
        extra_compile_args = extra_compile_args,
        include_dirs = include_dirs,
        extra_objects = extra_objects,
        define_macros = define_macros,
        )
    return metadata, ext_options

if __name__ == "__main__":
    sys.stderr.write("""You shouldn't be running this directly; it is used by setup.py.""")
    
