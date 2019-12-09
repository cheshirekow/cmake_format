# test: externalproject_add
ExternalProject_Add(
  foo_proj
  PREFIX ${CMAKE_BINARY_DIR}/foo/
  TMP_DIR ${CMAKE_BINARY_DIR}/foo/.tmp
  STAMP_DIR ${CMAKE_BINARY_DIR}/foo/.stamp
  LOG_DIR ${CMAKE_BINARY_DIR}/foo/.log
  DOWNLOAD_DIR ${CMAKE_BINARY_DIR}/foo/.download
  SOURCE_DIR ${CMAKE_BINARY_DIR}/foo/src
  BINARY_DIR ${CMAKE_BINARY_DIR}/foo/build
  INSTALL_DIR ${CMAKE_BINARY_DIR}/foo/install)

# test: externalproject_get_property
ExternalProject_Get_Property(foo_proj SOURCE_DIR BINARY_DIR)

# test: externalproject_add_step
ExternalProject_Add_Step(
  foo_proj hello_step
  COMMAND echo "hello world"
  COMMENT "say hello"
  DEPENDEES first_step
  DEPENDERS goodbye_step
  BYPRODUCTS hello.txt
  ALWAYS FALSE
  EXCLUDE_FROM_MAIN TRUE
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/foo
  LOG TRUE
  USES_TERMINAL FALSE)

# test: externalproject_add_steptargets
ExternalProject_Add_StepTargets(foo_proj NO_DEPENDS hello_step goodbye_step)

# test: externalproject_add_stepdependencies
ExternalProject_Add_StepDependencies(foo_proj hello_step target_one target_two)
