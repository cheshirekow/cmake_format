set(_copysrcs
    CHANGELOG.md
    images/cmake-format-logo.png
    images/small_demo.gif
    LICENSE
    package.json
    package-lock.json
    README.md
    src/extension.ts
    tsconfig.json
    tslint.json)

set(_copyfiles)
foreach(filename ${_copysrcs})
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
            ${CMAKE_CURRENT_BINARY_DIR}/${filename}
    DEPENDS ${filename}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  list(APPEND _copyfiles ${CMAKE_CURRENT_BINARY_DIR}/${filename})
endforeach()

# TODO(josh): glob the output tree so we can catch changes and accidental
# deletions
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/npm_install.stamp
  COMMAND npm install
  COMMAND touch npm_install.stamp
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS ${_copyfiles} package.json package-lock.json)

set(_baseImagesUrl "https://raw.githubusercontent.com/cheshirekow")
set(_baseImagesUrl "${_baseImagesUrl}/cmakelang/master/cmakelang")
set(_baseImagesUrl "${_baseImagesUrl}/vscode_extension")

add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/cmake-format-${_extension_version}.vsix
  COMMAND ${CMAKE_CURRENT_BINARY_DIR}/node_modules/vsce/out/vsce package
          --baseImagesUrl ${_baseImagesUrl}
  DEPENDS ${_copyfiles} ${CMAKE_CURRENT_BINARY_DIR}/npm_install.stamp
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

add_custom_target(
  vscode-extension
  DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/cmake-format-${_extension_version}.vsix)
