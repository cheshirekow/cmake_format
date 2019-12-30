# pylint: skip-file
"""
Database of known property names
"""

def get_regex():
  return re.compile("|".join(PATTERNS))

PATTERNS = [
  {%for pattern in patterns%}
    "{{pattern}}",
  {%-endfor%}
]

