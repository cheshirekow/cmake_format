set(programs
  catkin_find
  catkin_init_workspace
  catkin_package_version
  catkin_prepare_release
  catkin_test_results
  catkin_topological_order
  catkin_ws

  #catkin-build-debs-of-workspace
)

# generate relay-script for each program
foreach(program ${programs})
  set(EXECUTABLE ${catkin_SOURCE_DIR}/bin/${program})
  configure_file(${catkin_EXTRAS_DIR}/templates/script.sh.in
    ${CATKIN_BUILD_PREFIX}/${CATKIN_GLOBAL_BIN_DESTINATION}/${program}
    @ONLY)
endforeach()

# install all programs
install(PROGRAMS ${programs}
  DESTINATION ${CATKIN_GLOBAL_BIN_DESTINATION})
