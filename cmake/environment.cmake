function(detect_buildenv)
  if(DEFINED ENV{CI}
     AND DEFINED ENV{TRAVIS}
     AND "$ENV{CI}" STREQUAL "true"
     AND "$ENV{TRAVIS}" STREQUAL "true")
    set(IS_TRAVIS_CI TRUE PARENT_SCOPE)
  else()
    set(IS_TRAVIS_CI FALSE PARENT_SCOPE)
  endif()

  if(DEFINED ENV{TRAVIS_PULL_REQUEST}
     AND "$ENV{TRAVIS_PULL_REQUEST}" STREQUAL "true")
    set(IS_PULL_REQUEST TRUE PARENT_SCOPE)
  else()
    set(IS_PULL_REQUEST FALSE PARENT_SCOPE)
  endif()
endfunction()
