"""
Execute a GTK based program under broadway so that it can render without an
X backend.
"""

import argparse
import errno
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)


def pop_proc(procs, pid):
  for idx, proc in list(enumerate(procs)):
    if proc.pid == pid:
      return procs.pop(idx)
  raise ValueError("Unexpected pid: {}".format(pid))


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "-d", "--display-no", default=5, type=int,
      help="which display number the server should listen on")
  parser.add_argument(
      "--cwd", help="change to working directory to execute the program")
  parser.add_argument(
      "--executable",
      help="path to the binary to run, if the entry in argv[0] is different")
  parser.add_argument(
      "argv", nargs=argparse.REMAINDER)
  args = parser.parse_args()

  broadway = subprocess.Popen(["broadwayd", ":{:d}".format(args.display_no)])
  subenv = os.environ.copy()
  subenv["GDK_BACKEND"] = "broadway"
  subenv["BROADWAY_DISPLAY"] = ":{:d}".format(args.display_no)
  app = subprocess.Popen(
      args.argv, executable=args.executable, env=subenv, cwd=args.cwd)

  procs = [broadway, app]
  app_status = 1
  while procs:
    try:
      (pid, wstatus, _rusage) = os.wait4(-1, 0)
      pop_proc(procs, pid)
      if pid == app.pid:
        broadway.kill()
        app_status = wstatus

    except OSError as err:
      if err.errno == errno.EAGAIN:
        continue

      logger.exception("Error waiting for children")
      break

  if os.WIFEXITED(app_status):
    return os.WEXITSTATUS(app_status)
  if os.WIFSIGNALED(app_status):
    return -os.WSTOPSIG(app_status)
  return -1


if __name__ == "__main__":
  sys.exit(main())
