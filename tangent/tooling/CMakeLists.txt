add_custom_target(
  update-export
  COMMAND python -Bm tangent.tooling.export_sparse_subrepo update
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "Updating sparse export")

add_custom_target(
  verify-export
  COMMAND python -Bm tangent.tooling.export_sparse_subrepo verify
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  COMMENT "verify sparse export")

add_test(
  NAME verify-export
  COMMAND python -Bm tangent.tooling.export_sparse_subrepo verify
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
