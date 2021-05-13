"""
From one git worktree, synchronize the current code state with a sparse
checkout in another worktree.

Example usage::

  python -B tangent/tooling/sync_sparse.py \
    --match ${PWD} \
    --worktree ../tangent-sparse/protostruct \
    --sparse-config tangent/tooling/sparse-exports/protostruct

"""

import argparse
import logging
import os
import shutil
import subprocess


def get_toplevel(directory):
  """Return the worktree root directory for the worktree containing the
  given directory."""
  return subprocess.check_output(
      ["git", "rev-parse", "--show-toplevel"],
      cwd=directory).decode("utf-8").strip()


def get_gitdir(directory):
  """Return the .git directory location for the repository whose worktree
     contains the given directory."""
  return subprocess.check_output(
      ["git", "rev-parse", "--git-dir"],
      cwd=directory).decode("utf-8").strip()


def get_primary_repo(worktree):
  """Given a worktree root, find the git directory of the primary repository
     from which this worktree is managed."""
  git_dir = get_gitdir(worktree)
  parts = git_dir.split("/")
  if len(parts) < 3:
    return git_dir

  if parts[-2] == "worktrees":
    return "/".join(parts[:-2])

  return git_dir


def is_worktree(primary_repo, worktree):
  try:
    toplevel = get_toplevel(worktree)
  except OSError:
    return False

  try:
    current_primary_repo = get_primary_repo(worktree)
  except OSError:
    return False

  return toplevel == worktree and primary_repo == current_primary_repo


def ensure_worktree(primary_repo, worktree, commitish):
  """Ensure that the `worktree` directory is a worktree of `primary_repo`,
     checked-out at `commitish` in a clean/reset state."""

  if os.path.exists(worktree) and not os.path.isdir(worktree):
    os.remove(worktree)

  if not is_worktree(primary_repo, worktree):
    # Since we don't really know what the state is the easiest thing to do is
    # clear it out and reset it.
    if os.path.exists(worktree):
      shutil.rmtree(worktree)
    subprocess.check_call(
        ["git", "--git-dir", primary_repo,
         "worktree", "add", os.path.realpath(worktree), commitish])
    return

  current_sha1 = subprocess.check_output(
      ["git", "rev-parse", "HEAD"], cwd=worktree).decode("utf-8").strip()
  desired_sha1 = subprocess.check_output(
      ["git", "rev-parse", commitish], cwd=worktree).decode("utf-8").strip()

  if current_sha1 != desired_sha1:
    subprocess.check_output(
        ["git", "checkout", "--force", commitish], cwd=worktree)


def get_match(matchdir):
  head_sha1 = subprocess.check_output(
      ["git", "rev-parse", "HEAD"], cwd=matchdir).decode("utf-8").strip()

  return get_primary_repo(matchdir), head_sha1


def ensure_sparse(worktree, configdir):
  gitdir = get_gitdir(worktree)
  infodir = os.path.join(gitdir, "info")
  if not os.path.exists(infodir):
    os.makedirs(infodir)

  for filename in os.listdir(configdir):
    sourcepath = os.path.join(configdir, filename)
    if filename == "sparse-checkout":
      targetpath = os.path.join(infodir, "sparse-checkout")
    else:
      targetpath = os.path.join(worktree, filename)
    shutil.copyfile(sourcepath, targetpath)

  subprocess.check_call(["git", "checkout"], cwd=worktree)


def main():
  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--match", required=True)
  parser.add_argument(
      "--sparse-config", required=True,
      help="path to the directory containing sparse-checkout and others")
  parser.add_argument("--worktree", required=True)
  args = parser.parse_args()

  primary_repo, commitish = get_match(args.match)
  ensure_worktree(primary_repo, args.worktree, commitish)
  ensure_sparse(args.worktree, args.sparse_config)


if __name__ == "__main__":
  main()
