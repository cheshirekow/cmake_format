
if(CMAKE_LIBRARY_ARCHITECTURE)
  set(_matchme ".*${CMAKE_LIBRARY_ARCHITECTURE}/?$")
  if("${CMAKE_INSTALL_LIBDIR}" MATCHES ${_matchme})
    set(_libdir "${CMAKE_INSTALL_LIBDIR}")
  else()
    set(_libdir "${CMAKE_INSTALL_LIBDIR}/${CMAKE_LIBRARY_ARCHITECTURE}")
  endif()
else()
  set(_libdir "${CMAKE_INSTALL_LIBDIR}")
endif()

add_library(re2 STATIC IMPORTED GLOBAL)
set_property(TARGET re2 PROPERTY IMPORTED_LOCATION /usr/${_libdir}/libre2.a)
set_property(TARGET re2 PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES
                                 Threads::Threads)
add_library(re2-shared SHARED IMPORTED GLOBAL)
set_property(TARGET re2-shared PROPERTY IMPORTED_LOCATION
                                        /usr/${_libdir}/libre2.so)
set_property(TARGET re2-shared PROPERTY IMPORTED_LINK_INTERFACE_LIBRARIES
                                        Threads::Threads)
