with section("parse"):
  additional_commands = {
    "pkg_find": {
      "kwargs": {
        "PKG": "*"
      }
    },
    "format_and_lint": {
      "kwargs": {
        "CC": "*",
        "CCDEPENDS": "*",
        "CMAKE": "*",
        "PY": "*",
        "JS": "*",
        "EXCLUDE": "*"
      }
    }
  }
