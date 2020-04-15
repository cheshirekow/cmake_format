set(SUPPORTED_DISTRIBUTIONS xenial bionic eoan focal)
set(SUPPORTED_ARCHITECTURES amd64 arm64 i386)

set(_this_distro)
if(EXISTS "/etc/lsb-release")
  file(STRINGS "/etc/lsb-release" _lines)
  foreach(line ${_lines})
    if("${line}" MATCHES "^([^=]+)=(.+)")
      if("${CMAKE_MATCH_1}" STREQUAL "DISTRIB_CODENAME")
        set(_this_distro "${CMAKE_MATCH_2}")
        break()
      endif()
    endif()
  endforeach()
else()
  message(INFO "Can't query lsb-release")
endif()
set_property(GLOBAL PROPERTY NATIVE_DISTRIBUTION ${_this_distro})

execute_process(
  COMMAND dpkg --print-architecture
  RESULT_VARIABLE _returncode
  OUTPUT_VARIABLE _this_arch
  ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE)
if(NOT _returncode EQUAL 0)
  message(WARNING "Failed to query current distribution architecture")
endif()
set_property(GLOBAL PROPERTY NATIVE_ARCHITECTURE ${_this_arch})

foreach(_distro ${SUPPORTED_DISTRIBUTIONS})
  add_custom_target(${_distro}-source-packages)
  foreach(_arch ${SUPPORTED_ARCHITECTURES})
    add_custom_target(debs-${_distro}-${_arch})
  endforeach()
  if(_this_arch)
    add_custom_target(debs-${_distro})
    add_dependencies(debs-${_distro} debs-${_distro}-${_this_arch})
  endif()
endforeach()

if(_this_distro AND _this_arch)
  add_custom_target(debs)
  add_dependencies(debs debs-${_this_distro}-${_this_arch})
endif()

check_call(COMMAND id -u OUTPUT_VARIABLE _uid)
set(_sudo)
if(NOT "${_uid}" EQUAL "0")
  set(_sudo "sudo")
endif()

# Return in ${outvar} a list of command line options added to the debuild
# command in order to sign the package. If DEBIAN_SIGNING_KEY is define it will
# return flags used to sign with that key. If it is not defined, it will return
# flags used to skip signing.
function(get_signing_flags outvar)
  if(DEBIAN_SIGNING_KEY)
    # e.g. 6A8A4FAF
    set(${outvar}
        -sa -pgpg2 -k${DEBIAN_SIGNING_KEY}
        PARENT_SCOPE)
  else()
    # NOTE(josh):
    #
    # * -uc, --unsigned-changes
    # * -us, --unsigned-source
    set(${outvar}
        -uc -us
        PARENT_SCOPE)
  endif()
endfunction()

# Given a list of variable names in the current scope, save them all as
# properties
#
# Usage:
# ~~~
# exportvars(<prop-spec> VARS <var1> [<var2 [...]])
# ~~~
#
# Example:
# ~~~
# exportvars(DIRECTORY VARS foo bar baz)
# ~~~
macro(exportvars)
  cmake_parse_arguments(_args "" "" "VARS" ${ARGN})

  foreach(varname ${_args_VARS})
    set_property(${_args_UNPARSED_ARGUMENTS} PROPERTY ${varname}
                                                      "${${varname}}")
  endforeach()
endmacro()

# Retrieve a list of properites as variables with the same in the current scope
#
# Usage:
# ~~~
# importvars(<prop-spec> VARS <var1> [<var2 [...]])
# ~~~
#
# Example:
# ~~~
# importvars(DIRECTORY VARS foo bar baz)
# ~~~
macro(importvars)
  cmake_parse_arguments(_args "" "" "VARS" ${ARGN})

  foreach(varname ${_args_VARS})
    get_property(${varname} ${_args_UNPARSED_ARGUMENTS} PROPERTY ${varname})
  endforeach()
endmacro()

# Return the path to the pbuilder base image tarball for the given `distro` and
# `arch`.
function(get_pbuilder_basetgz outvar distro arch)
  set(${outvar}
      /var/cache/pbuilder/${_distro}-${_arch}-base.tgz
      PARENT_SCOPE)
endfunction()

# Add a rule to generate the pbuilder base image tarball for the given `distro`
# and `arch`.
function(pbuilder_create distro arch)
  get_pbuilder_basetgz(_basetgz ${distro} ${arch})
  add_custom_command(
    OUTPUT ${_basetgz}
    COMMAND
      ${_sudo} pbuilder create --distribution ${distro} #
      --architecture ${arch} --basetgz ${_basetgz} #
      --hookdir ${CMAKE_SOURCE_DIR}/debian/pbuilder-hooks #
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Bootstraping base tgz for ${distro}/${arch}")
  add_custom_target(pbuilder-basetgz-${distro}-${arch} DEPENDS ${_basetgz})
endfunction()

# Run the debhelp python script, write the output to a unique file, then include
# the result file into the current cmake scope, executing it inline.
#
# Usage:
# ~~~
# debhelp(<command> [arg1 [arg2 [...]]])
# ~~~
set_property(GLOBAL PROPERTY DEBHELP_INCLUDENO 0)
macro(debhelp command)
  get_property(_includeno GLOBAL PROPERTY DEBHELP_INCLUDENO)
  math(EXPR _includeno "${_includeno} + 1")
  set_property(GLOBAL PROPERTY DEBHELP_INCLUDENO ${_includeno})

  set(_stubfile ${CMAKE_BINARY_DIR}/debian/debhelp-${_includeno}.cmake)
  execute_process(
    COMMAND python -Bm tangent.tooling.debhelp -o ${_stubfile} ${command}
            ${ARGN}
    RESULT_VARIABLE _returncode
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
  if(NOT _returncode EQUAL 0)
    message(FATAL_ERROR "Failed to execute debhelp ${command}")
  endif()
  include(${_stubfile} RESULT_VARIABLE _result)
  if(_result EQUAL NOTFOUND)
    message(FATAL_ERROR "Failed to include debhelp stubfile ${_stubfile}")
  endif()
endmacro()

# Run the debhelp python script to parse the changelog
#
# Usage:
# ~~~
# debhelp_parse_changelog(<filepath> <prefix>)
# ~~~
#
# Returns the following variables into the callers scope:
#
# * <prefix>_package: debian package name
# * <prefix>_version: upstream package version
# * <prefix>_debversion: debian version suffix
function(debhelp_parse_changelog filepath prefix)
  debhelp(parse-changelog ${filepath} ${prefix})
  # Enforces cmake re-run if the changelog changes. This is required because the
  # version number might have changed and we'll need to reparse it.
  configure_file(${filepath}
                 ${CMAKE_BINARY_DIR}/debhelp/parse-stamps/${filepath} COPYONLY)
  exportvars(DIRECTORY VARS ${prefix}_package ${prefix}_version
                            ${prefix}_debversion)
endfunction()

# Create the "upstream" tarball used to generate a debian package. The tarball
# contains all of the "exported" sources as specified by a list of glob patterns
# in a file
#
# Usage:
# ~~~
# create_debian_tarball(<name>)
# ~~~
#
# Where `name` is a subdirectory of `debian/exports`.
function(create_debian_tarball name)
  importvars(DIRECTORY VARS ${name}_package ${name}_version ${name}_debversion)
  set(_basename ${${name}_package}_${${name}_version})
  set(_patterns_path
      ${CMAKE_CURRENT_SOURCE_DIR}/exports/${name}/debian/sources.txt)
  set(_manifest_path ${CMAKE_CURRENT_BINARY_DIR}/${name}.manifest)
  set(_debfiles_path ${CMAKE_CURRENT_BINARY_DIR}/${name}.debfiles)

  # Parse the sources.txt include globs and build a manifest of what source
  # files to include in the tarball. Save this to ${_manifest_path}
  add_custom_target(
    deb-chkmanifest-${name}
    COMMAND
      python -Bm tangent.tooling.debhelp #
      --outpath ${_manifest_path} #
      check-manifest --patterns-from ${_patterns_path} ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    BYPRODUCTS ${_manifest_path}
    COMMENT "Checking source manifest for ${name}")

  if(NOT ${CMAKE_GENERATOR} STREQUAL Ninja)
    add_custom_command(
      OUTPUT ${_manifest_path}
      DEPENDS deb-chkmanifest-${name}
      COMMENT "Stubbing source manifest for ${name}")
  endif()

  # Glob the common/debian and exports/${name}/debian directories to get a list
  # of files that go in the debian/ directory of the tarball
  add_custom_target(
    deb-chkdebfiles-${name}
    COMMAND
      python -Bm tangent.tooling.debhelp #
      --outpath ${_debfiles_path} #
      check-manifest --patterns common/debian/* exports/${name}/debian/* --
      ${CMAKE_CURRENT_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    BYPRODUCTS ${_debfiles_path}
    COMMENT "Checking debian files manifest for ${name}")

  if(NOT ${CMAKE_GENERATOR} STREQUAL Ninja)
    add_custom_command(
      OUTPUT ${_debfiles_path}
      DEPENDS deb-chkdebfiles-${name}
      COMMENT "Stubbing debian files manifest for ${name}")
  endif()

  # Create the source tarball. We do this just once and then simlink it into the
  # different distribution directoreies.
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${_basename}.orig.tar.gz
    COMMAND
      tar --create --gzip #
      --file=${CMAKE_CURRENT_BINARY_DIR}/${_basename}.orig.tar.gz #
      --transform 's,^,${_basename}/,' #
      --directory ${CMAKE_CURRENT_SOURCE_DIR}/common . #
      --directory ${CMAKE_CURRENT_SOURCE_DIR}/exports/${name} . #
      --directory ${CMAKE_SOURCE_DIR} --files-from ${_manifest_path}
    DEPENDS ${_manifest_path} ${_debfiles_path}
    COMMENT "Creating source tarball ${_basename}.orig.tar.gz"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endfunction()

# Create a debian source package by translating the changelog from a generic
# channel name to an ubuntu-suite channel name and then running debuild
#
# Usage:
# ~~~
# create_debian_source_package(<name> <distro>)
# ~~~
#
# Where `name` is a subdirectory of `debian/exports` and `distro` is an valid
# ubuntu codename (xenial, bionic, focal).
function(create_debian_source_package name distro)
  importvars(DIRECTORY VARS ${name}_package ${name}_version ${name}_debversion)
  set(_basename ${${name}_package}_${${name}_version})
  set(_outdir ${CMAKE_CURRENT_BINARY_DIR}/${distro})
  set(_changelog ${CMAKE_CURRENT_SOURCE_DIR}/exports/${name}/debian/changelog)

  # Create a symlink to the upstream tarball within the distro-specific working
  # directory
  add_custom_command(
    OUTPUT ${_outdir}/${_basename}.orig.tar.gz
    COMMAND ${CMAKE_COMMAND} -E make_directory ${_outdir}
    COMMAND ${CMAKE_COMMAND} -E create_symlink ../${_basename}.orig.tar.gz
            ${_outdir}/${_basename}.orig.tar.gz
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Creating ${distro} symlink to upstream tarball for ${name}"
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${_basename}.orig.tar.gz)

  # These are all the files that are created by debuild
  set(_outputs
      ${_outdir}/${_basename}-${${name}_debversion}~${distro}.debian.tar.xz
      ${_outdir}/${_basename}-${${name}_debversion}~${distro}.dsc
      ${_outdir}/${_basename}-${${name}_debversion}~${distro}_source.build
      ${_outdir}/${_basename}-${${name}_debversion}~${distro}_source.buildinfo
      ${_outdir}/${_basename}-${${name}_debversion}~${distro}_source.changes)

  get_signing_flags(_signflags)

  # Extract the upstream source tarball, translate the changelog, and run
  # debbuild
  add_custom_command(
    OUTPUT ${_outputs}
    # This is the directory where the upstream tarball will be extracted. We
    # need to delete it so that we don't have any stale files
    COMMAND rm -rf ${_outdir}/${_basename}
    COMMAND tar --directory ${_outdir} --extract --gzip
            --file=${_outdir}/${_basename}.orig.tar.gz
    # Copy the changelog to the distro-specific destination and replace the
    # distribution name
    COMMAND
      python -Bm tangent.tooling.debhelp translate-changelog #
      --src ${_changelog} #
      --tgt ${_outdir}/${_basename}/debian/changelog #
      --distro ${distro}
    COMMAND
      cd ${_outdir}/${_basename} #
      && debuild -S -d ${_signflags} > ../${_basename}.debuild1.log ||
      (cat ../${_basename}.debuild1.log && false)
    DEPENDS ${_outdir}/${_basename}.orig.tar.gz
    COMMENT "Creating ${distro} source package for ${name}"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_custom_target(
    dput-${name}-${distro}
    COMMAND
      dput ppa:josh-bialkowski/tangent
      ${_outdir}/${_basename}-${${name}_debversion}~${distro}_source.changes
    DEPENDS ${_outputs})

  add_custom_target(deb-src-${name}-${distro} DEPENDS ${_outputs})
  add_dependencies(${distro}-source-packages deb-src-${name}-${distro})
endfunction()

# Create debian binary packages from the debian source package for `name`.
#
# Usage:
# ~~~
# create_debian_binary_packages(
#   <tag> <distro> <arch> <binpkg1> [<binpkg2> [...]])
# ~~~
function(create_debian_binary_packages tag distro arch)
  cmake_parse_arguments(_args "FORCE_PBUILDER" "" "OUTPUTS;DEPS" ${ARGN})

  importvars(GLOBAL VARS NATIVE_DISTRIBUTION NATIVE_ARCHITECTURE)
  set(_outdir ${CMAKE_CURRENT_BINARY_DIR}/${distro})
  set(_basename "${${tag}_package}_${${tag}_version}")
  set(_version "${${tag}_version}-${${tag}_debversion}~${distro}")

  get_pbuilder_basetgz(_basetgz ${distro} ${arch})

  # This is a directory where we will copy all of the dependant debian packages
  # and construct a local filesystem debian repository.
  set(_depsrepo ${CMAKE_CURRENT_BINARY_DIR}/${distro}/${arch}/${tag}-deps)

  # Given a list of all the dependant projects, construct a list of all the .deb
  # files that we depend on
  set(_deb_depends)
  foreach(_deptag ${_args_DEPS})
    get_property(_deblist GLOBAL PROPERTY deblist-${_deptag}-${distro}-${arch})
    list(APPEND _deb_depends ${_deblist})
  endforeach()

  # Create rules to copy all our dependant .deb files into a single directory
  # which we will bind to the pbuilder chroot as a filesystem debian repository.
  set(_repo_debs)
  foreach(_deb ${_deb_depends})
    get_filename_component(_filename ${_deb} NAME)
    # NOTE(josh): we add the deps/ path suffix so that at least one component is
    # in-common with the bindmount location. We'll need this to generate correct
    # file paths in the Packages file.
    set(_repo_deb ${_depsrepo}/deps/${_filename})
    add_custom_command(
      OUTPUT ${_repo_deb}
      COMMAND ${CMAKE_COMMAND} -E copy ${_deb} ${_repo_deb}
      DEPENDS ${_deb})
    list(APPEND _repo_debs ${_repo_deb})
  endforeach()

  # Create a rule to generate the debian `Packages` file indexing the packages
  # of our filesystem debian repository.
  add_custom_command(
    OUTPUT ${_depsrepo}/deps/Packages
    COMMAND dpkg-scanpackages . > Packages
    # NOTE(josh): the following is equivalent. I'm not sure which tool is better
    # to use??
    #
    # COMMAND apt-ftparchive packages . > Packages
    WORKING_DIRECTORY ${_depsrepo}/deps
    DEPENDS ${_repo_debs}
    COMMENT "Creating depsrepo for ${tag}")

  get_signing_flags(_signflags)

  # ${_outputs} contains a list of all the files that are generated as part of
  # the binary packages build. It is generated from the `OUTPUTS` keyword
  # argument by prepending the output directory and appending the version and
  # architecture suffixes.
  set(_outputs)
  foreach(_binpkg ${_args_OUTPUTS})
    set(_debname ${_binpkg}_${_version}_${arch}.deb)
    list(APPEND _outputs ${_outdir}/${_debname})
  endforeach()

  if("${distro}" STREQUAL "${NATIVE_DISTRIBUTION}" #
     AND "${arch}" STREQUAL "${NATIVE_ARCHITECTURE}"
     AND NOT ${_args_FORCE_PBUILDER}
     AND NOT _args_DEPS)
    add_custom_command(
      OUTPUT ${_outputs}
      # NOTE(josh): add the -nc, --no-pre-clean option to reuse the existing
      # build directory for an incremental build.
      COMMAND debuild -b ${_signflags} > ${_outdir}/${_basename}.debuild2.log ||
              (cat ${_outdir}/${_basename}.debuild2.log && false)
      WORKING_DIRECTORY ${_outdir}/${_basename}
      DEPENDS ${_outdir}/${_basename}.orig.tar.gz
              ${_outdir}/${_basename}-${${tag}_debversion}~${distro}.dsc
      COMMENT "Creating (native) binary packages for ${tag}")
  else()
    add_custom_command(
      OUTPUT ${_outputs}
      COMMAND
        ${_sudo} env DEB_BUILD_OPTIONS="parallel=8" #
        pbuilder build --distribution #
        ${distro} --architecture ${arch} --basetgz ${_basetgz} #
        --buildresult ${CMAKE_CURRENT_BINARY_DIR}/${distro} #
        --hookdir ${CMAKE_CURRENT_SOURCE_DIR}/pbuilder-hooks #
        --bindmounts "${_depsrepo}/deps:/var/cache/pbuilder/deps" #
        --loglevel W #
        --logfile ${_outdir}/${_basename}.pbuild.log #
        ${_outdir}/${_basename}-${${tag}_debversion}~${distro}.dsc #
        > /dev/null #
        || (cat ${_outdir}/${_basename}.pbuild.log && false)
      DEPENDS ${_outdir}/${_basename}.orig.tar.gz
              ${_outdir}/${_basename}-${${tag}_debversion}~${distro}.dsc
              ${_basetgz} ${_depsrepo}/deps/Packages
      COMMENT "Creating ${distro}/${arch} (pbuilder) binary pkgs for ${tag}")
  endif()

  add_custom_target(debs-${tag}-${distro}-${arch} DEPENDS ${_outputs})
  add_dependencies(debs-${distro}-${arch} debs-${tag}-${distro}-${arch})
  set_property(GLOBAL PROPERTY deblist-${tag}-${distro}-${arch} ${_outputs})
endfunction()

# Entry point into the debian package build system. The build system is roughly
# summarized as:
#
# 1. Parse the changelog to get version numbers
# 2. Create an "upstream" tarball
# 3. Foreach distribution: a. Create a debian source package b. Foreach
#    architecture: i. create debian binary packages
#
# Usage:
# ~~~
# create_debian_packages(<tag> <binpkg1> [<binpkg2> [...]])
# ~~~
function(create_debian_packages tag)
  set(_changelog ${CMAKE_CURRENT_SOURCE_DIR}/exports/${tag}/debian/changelog)
  debhelp_parse_changelog(${_changelog} ${tag})
  create_debian_tarball(${tag})

  importvars(DIRECTORY VARS ${tag}_package ${tag}_version ${tag}_debversion)

  foreach(_distro ${SUPPORTED_DISTRIBUTIONS})
    create_debian_source_package(${tag} ${_distro})
    foreach(_arch ${SUPPORTED_ARCHITECTURES})
      create_debian_binary_packages(${tag} ${_distro} ${_arch} ${ARGN})
    endforeach()
  endforeach()
endfunction()

foreach(_distro ${SUPPORTED_DISTRIBUTIONS})
  foreach(_arch ${SUPPORTED_ARCHITECTURES})
    pbuilder_create(${_distro} ${_arch})
  endforeach()
endforeach()

# Return in ${outvar} a list of all the binary packages produced by the list of
# slugs.
#
# Usage:
# ~~~
#   get_debs(<outvar> <distro> <arch> <slug1> [<slug2> [<slug3> [...]]])
# ~~~
function(get_debs outvar distro arch)
  set(_deb_depends)
  foreach(_slug tangent-util json argue linkhash)
    get_property(_deblist GLOBAL PROPERTY deblist-${_slug}-${distro}-${arch})
    list(APPEND _deb_depends ${_deblist})
  endforeach()
  set(${outvar}
      ${_deb_depends}
      PARENT_SCOPE)
endfunction()
