import sys
import platform
running_os = platform.system()
if running_os.lower() in ('linux', 'darwin'):
    from fvid import main
else:
    from fvid.fvid import main

if __name__ == '__main__':
	sys.exit(main())
