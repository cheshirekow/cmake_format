import collections
import logging

from cmake_lint import lintdb

logger = logging.getLogger(__name__)


class LintRecord(object):
  """Records an instance of lint at a particular location
  """

  def __init__(self, spec, location, msg):
    self.spec = spec
    self.location = location
    self.msg = msg

  def __repr__(self):
    if self.location is None:
      return " [{:s}] {:s}".format(self.spec.idstr, self.msg)

    if isinstance(self.location, tuple):
      return "{:s}: [{:s}] {:s}".format(
          ",".join("{:02d}".format(val) for val in self.location[:2]),
          self.spec.idstr, self.msg)

    raise ValueError(
        "Unexpected type {} for location".format(type(self.location)))


class FileContext(object):
  def __init__(self, global_ctx, infile_path):
    self.global_ctx = global_ctx
    self.infile_path = infile_path
    self.config = None
    self._lint = []
    self._supressions = set()
    self._supressed_count = collections.defaultdict(int)

  def is_idstr(self, idstr):
    return idstr in self.global_ctx.lintdb

  def supress(self, idlist):
    """
    Given a list of lint ids, enable a supression for each one which is not
    already supressed. Return the list of new supressions
    """
    new_supressions = []
    for idstr in idlist:
      if idstr in self._supressions:
        continue
      self._supressions.add(idstr)
      new_supressions.append(idstr)

    return new_supressions

  def unsupress(self, idlist):
    for idstr in idlist:
      if idstr not in self._supressions:
        logger.warning(
            "Unsupressing %s which is not currently surpressed", idstr)
      self._supressions.discard(idstr)

  def record_lint(self, idstr, *args, **kwargs):
    if idstr in self.config.linter.disabled_codes:
      self._supressed_count[idstr] += 1
      return

    if idstr in self._supressions:
      self._supressed_count[idstr] += 1
      return

    spec = self.global_ctx.lintdb[idstr]
    location = kwargs.pop("location", ())
    msg = spec.msgfmt.format(*args, **kwargs)
    record = LintRecord(spec, location, msg)
    self._lint.append(record)

  def get_lint(self):
    """Return lint records in sorted order"""
    return [
        record for _, _, _, record in sorted(
            (record.location, record.spec.idstr, idx, record)
            for idx, record in enumerate(self._lint))]

  def writeout(self, outfile):
    for record in self.get_lint():
      outfile.write("{:s}:{}\n".format(self.infile_path, record))

  def has_lint(self):
    return bool(self._lint)


class GlobalContext(object):
  category_names = {
      "C": "Convention",
      "E": "Error",
      "R": "Refactor",
      "W": "Warning",
  }

  def __init__(self, outfile):
    self.outfile = outfile
    self.lintdb = lintdb.get_database()
    self.file_ctxs = {}

  def get_file_ctx(self, infile_path, config):
    if infile_path not in self.file_ctxs:
      self.file_ctxs[infile_path] = FileContext(self, infile_path)
    ctx = self.file_ctxs[infile_path]
    ctx.config = config
    return ctx

  def get_category_counts(self):
    lint_counts = {}
    for _, file_ctx in sorted(self.file_ctxs.items()):
      for record in file_ctx.get_lint():
        category_char = record.spec.idstr[0]
        if category_char not in lint_counts:
          lint_counts[category_char] = 0
        lint_counts[category_char] += 1
    return lint_counts

  def write_summary(self, outfile):
    outfile.write("Summary\n=======\n")
    outfile.write("files scanned: {:d}\n".format(len(self.file_ctxs)))
    outfile.write("found lint:\n")

    lint_counts = self.get_category_counts()
    fieldwidth = max(len(name) for _, name in self.category_names.items())
    fmtstr = "  {:>" + str(fieldwidth) + "s}: {:d}\n"
    for (category_char, count) in sorted(lint_counts.items()):
      category_name = self.category_names[category_char]
      outfile.write(fmtstr.format(category_name, count))
    outfile.write("\n")
