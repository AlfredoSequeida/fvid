import sys

# leaving this here in case the try/except thing doesn't work
"""
import platform
import distro # to check linux distributions

try:
    linux_distro = distro.linux_distribution()[0].lower()
except:
    linux_distro = "n/a"

# fvid 
if platform.system().lower() in ('linux', 'darwin') and linux_distro not in ('artix linux',):
    # this used to work for every distro but something changed in the Cython/Password PR
    from fvid import main
else:
    # windows and artix linux need this because of something in the Cython/Password PR, unknown if more OSes need it
    from fvid.fvid import main
"""

try:
    from fvid import main
except:
    from fvid.fvid import main

if __name__ == '__main__':
    sys.exit(main())
