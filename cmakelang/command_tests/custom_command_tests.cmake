# test: legacy_spec
#[=[
additional_commands = {
  "foo": {
    "flags": ["BAR", "BAZ"],
    "kwargs": {
      "HEADERS": "*",
      "SOURCES": "*",
      "DEPENDS": "*"
    }
  }
}
]=]
foo(nonkwarg_a nonkwarg_b
    HEADERS a.h b.h c.h d.h e.h f.h
    SOURCES a.cc b.cc d.cc
    DEPENDS foo
    bar baz)

# test: new_spec_dict
#[=[
additional_commands = {
  "foo": {
    "pargs": {
      "flags": ["BAR", "BAZ"],
      "legacy": True,
    },
    "kwargs": {
      "HEADERS": "*",
      "SOURCES": "*",
      "DEPENDS": "*"
    }
  }
}
]=]
foo(nonkwarg_a nonkwarg_b
    HEADERS a.h b.h c.h d.h e.h f.h
    SOURCES a.cc b.cc d.cc
    DEPENDS foo
    bar baz)

# test: new_spec_list
#[=[
additional_commands = {
  "foo": {
    "pargs": [{
      "flags": ["BAR", "BAZ"],
      "legacy": True,
    }],
    "kwargs": {
      "HEADERS": "*",
      "SOURCES": "*",
      "DEPENDS": "*"
    }
  }
}
]=]
foo(nonkwarg_a nonkwarg_b bar baz
    HEADERS a.h b.h c.h d.h e.h f.h
    SOURCES a.cc b.cc d.cc
    DEPENDS foo)

# test: new_spec_arg_kwargs
#[=[
additional_commands = {
  "foo": {
    "pargs": [["*", {
      "flags": ["BAR", "BAZ"],
      "legacy": True,
    }]],
    "kwargs": {
      "HEADERS": "*",
      "SOURCES": "*",
      "DEPENDS": "*"
    }
  }
}
]=]
foo(nonkwarg_a nonkwarg_b
    HEADERS a.h b.h c.h d.h e.h f.h
    SOURCES a.cc b.cc d.cc
    DEPENDS foo
    bar baz)

# test: new_spec_multiple
#[=[
additional_commands = {
  "foo": {
    "pargs": ["*", {"flags": ["BAR", "BAZ"]}],
    "kwargs": {
      "HEADERS": "*",
      "SOURCES": "*",
      "DEPENDS": "*"
    }
  }
}
]=]
foo(nonkwarg_a nonkwarg_b
    HEADERS a.h b.h c.h d.h e.h f.h
    SOURCES a.cc b.cc d.cc
    DEPENDS foo
    bar baz)

# test: custom_cmdline
#[=[
additional_commands = {
  "mything": {
    "kwargs": {
      "MYCOMMAND": {
        "pargs": {
          "tags": ["cmdline"]
        }
      }
    }
  }
}
]=]
mything(
  foo bar baz
  MYCOMMAND
    this is a sequence of arguments that are passed to the shell as a command
    and should not be wrapped even though the sequence is very long)
