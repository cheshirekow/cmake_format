# test: kwarg_match_consumes
install(TARGETS myprog RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
                               COMPONENT runtime)

# test: install_targets
#[=[
expect_parse = [
  (NodeType.BODY, [
    (NodeType.STATEMENT, [
      (NodeType.FUNNAME, []),
      (NodeType.LPAREN, []),
      (NodeType.ARGGROUP, [
        (NodeType.KWARGGROUP, [
          (NodeType.KEYWORD, []),
          (NodeType.PARGGROUP, [
            (NodeType.ARGUMENT, []),
          ]),
        ]),
        (NodeType.KWARGGROUP, [
          (NodeType.KEYWORD, []),
          (NodeType.PARGGROUP, [
            (NodeType.ARGUMENT, []),
          ]),
        ]),
        (NodeType.KWARGGROUP, [
          (NodeType.KEYWORD, []),
          (NodeType.ARGGROUP, [
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
          ]),
        ]),
        (NodeType.KWARGGROUP, [
          (NodeType.KEYWORD, []),
          (NodeType.ARGGROUP, [
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
          ]),
        ]),
        (NodeType.KWARGGROUP, [
          (NodeType.KEYWORD, []),
          (NodeType.ARGGROUP, [
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
            (NodeType.KWARGGROUP, [
              (NodeType.KEYWORD, []),
              (NodeType.PARGGROUP, [
                (NodeType.ARGUMENT, []),
              ]),
            ]),
          ]),
        ]),
      ]),
      (NodeType.RPAREN, []),
    ]),
    (NodeType.WHITESPACE, []),
  ]),
]
]=]
install(
  TARGETS ${PROJECT_NAME}
  EXPORT ${CMAKE_PROJECT_NAME}Targets
  ARCHIVE DESTINATION lib COMPONENT install-app
  LIBRARY DESTINATION lib COMPONENT install-app
  RUNTIME DESTINATION bin COMPONENT install-app)