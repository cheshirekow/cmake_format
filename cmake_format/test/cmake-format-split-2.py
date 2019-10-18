# pylint: disable=invalid-name
# Additional FLAGS and KWARGS for custom commands
additional_commands = {
    "foo": {
        "flags": ["BAR", "BAZ"],
        "kwargs": {
            "HEADERS": '*',
            "SOURCES": '*',
            "DEPENDS": '*',
        }
    }
}
