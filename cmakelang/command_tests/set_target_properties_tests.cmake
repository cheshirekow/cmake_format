# test: format_pairs
set_target_properties(
  ${PROJECT_NAME}
  PROPERTIES C_STANDARD 11
             C_STANDARD_REQUIRED YES
             C_EXTENSIONS YES
             CXX_STANDARD 17
             CXX_STANDARD_REQUIRED YES
             CXX_EXTENSIONS YES
             COMPILE_FLAGS -Wunused)

