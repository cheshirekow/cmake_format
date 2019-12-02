"""
Database of known variable names
"""

def get_regex():
  return re.compile("|".join(PATTERNS))

PATTERNS = [
  {%for pattern in patterns%}
    "{{pattern}}",
  {%-endfor%}
]

