set(SUPPORTED_DISTRIBUTIONS xenial bionic eoan focal)
set(SUPPORTED_ARCHITECTURES amd64 arm64 i386)

set_property(GLOBAL PROPERTY DEBIAN_SUPPORTED_DISTRIBUTIONS
                             ${SUPPORTED_DISTRIBUTIONS})
set_property(GLOBAL PROPERTY DEBIAN_SUPPORTED_ARCHITECTURES
                             ${SUPPORTED_ARCHITECTURES})

foreach(distro ${SUPPORTED_DISTRIBUTIONS})
  add_custom_target(${distro}-source-packages)
  foreach(arch ${SUPPORTED_ARCHITECTURES})
    add_custom_target(debs-${distro}-${arch})
  endforeach()
  if(BUILDENV_DPKG_ARCHITECTURE)
    add_custom_target(debs-${distro})
    add_dependencies(debs-${distro}
                     debs-${distro}-${BUILDENV_DPKG_ARCHITECTURE})
  endif()
endforeach()

if(BUILDENV_DISTRIB_CODENAME AND BUILDENV_DPKG_ARCHITECTURE)
  add_custom_target(debs)
  add_dependencies(
    debs debs-${BUILDENV_DISTRIB_CODENAME}-${BUILDENV_DPKG_ARCHITECTURE})
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
# EXPORTVARS(<prop-spec> VARS <var1> [<var2 [...]])
# ~~~
#
# Example:
# ~~~
# EXPORTVARS(DIRECTORY VARS foo bar baz)
# ~~~
macro(EXPORTVARS)
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
# IMPORTVARS(<prop-spec> VARS <var1> [<var2 [...]])
# ~~~
#
# Example:
# ~~~
# IMPORTVARS(DIRECTORY VARS foo bar baz)
# ~~~
macro(IMPORTVARS)
  cmake_parse_arguments(_args "" "" "VARS" ${ARGN})

  foreach(varname ${_args_VARS})
    get_property(${varname} ${_args_UNPARSED_ARGUMENTS} PROPERTY ${varname})
  endforeach()
endmacro()

# Return the path to the pbuilder base image tarball for the given `distro` and
# `arch`.
function(get_pbuilder_basetgz outvar distro arch)
  set(${outvar}
      /var/cache/pbuilder/${distro}-${arch}-base.tgz
      PARENT_SCOPE)
endfunction()

add_custom_target(
  check-pbuilder-rc
  COMMAND python -B ${TANGENT_TOOLING}/check_pbuilderrc.py
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# Add a rule to generate the pbuilder base image tarball for the given `distro`
# and `arch`.
function(pbuilder_create distro arch)
  get_pbuilder_basetgz(_basetgz ${distro} ${arch})
  add_custom_command(
    OUTPUT ${_basetgz}
    DEPENDS check-pbuilder-rc
    COMMAND
      ${_sudo} pbuilder create --distribution ${distro} #
      --architecture ${arch} --basetgz ${_basetgz} #
      --hookdir ${CMAKE_SOURCE_DIR}/debian/pbuilder-hooks #
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Bootstraping base tgz for ${distro}/${arch}")
  add_custom_target(pbuilder-basetgz-${distro}-${arch} DEPENDS ${_basetgz})
endfunction()

set_property(GLOBAL PROPERTY DEBHELP_INCLUDENO 0)

# Run the debhelp python script, write the output to a unique file, then include
# the result file into the current cmake scope, executing it inline.
#
# Usage:
# ~~~
# debhelp(<command> [arg1 [arg2 [...]]])
# ~~~
macro(DEBHELP command)
  get_property(_includeno GLOBAL PROPERTY DEBHELP_INCLUDENO)
  math(EXPR _includeno "${_includeno} + 1")
  set_property(GLOBAL PROPERTY DEBHELP_INCLUDENO ${_includeno})

  set(_stubfile ${CMAKE_BINARY_DIR}/debian/debhelp-${_includeno}.cmake)
  execute_process(
    COMMAND python -B ${TANGENT_TOOLING}/debhelp.py -o ${_stubfile} ${command}
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
# debhelp_parsechangelog(<filepath> <prefix>)
# ~~~
#
# Returns the following variables into the callers scope:
#
# * <prefix>_package: debian package name
# * <prefix>_version: upstream package version
# * <prefix>_debversion: debian version suffix
function(debhelp_parsechangelog filepath prefix)
  DEBHELP(parse-changelog ${filepath} ${prefix})
  # Enforces cmake re-run if the changelog changes. This is required because the
  # version number might have changed and we'll need to reparse it.
  configure_file(${filepath}
                 ${CMAKE_BINARY_DIR}/debhelp/parse-stamps/${filepath} COPYONLY)
  EXPORTVARS(DIRECTORY VARS ${prefix}_package ${prefix}_version
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
  IMPORTVARS(DIRECTORY VARS ${name}_package ${name}_version ${name}_debversion)
  set(basename ${${name}_package}_${${name}_version})
  set(common_patterns_path
      ${CMAKE_CURRENT_SOURCE_DIR}/common/debian/sources.txt)
  set(patterns_path
      ${CMAKE_CURRENT_SOURCE_DIR}/exports/${name}/debian/sources.txt)
  set(manifest_path ${CMAKE_CURRENT_BINARY_DIR}/${name}.manifest)
  set(debfiles_path ${CMAKE_CURRENT_BINARY_DIR}/${name}.debfiles)

  # Parse the sources.txt include globs and build a manifest of what source
  # files to include in the tarball. Save this to ${manifest_path}
  add_custom_target(
    deb-chkmanifest-${name}
    COMMAND
      python -B ${TANGENT_TOOLING}/debhelp.py #
      --outpath ${manifest_path} #
      check-manifest --patterns-from ${common_patterns_path} --patterns-from
      ${patterns_path} ${CMAKE_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    BYPRODUCTS ${manifest_path}
    COMMENT "Checking source manifest for ${name}")

  if(NOT ${CMAKE_GENERATOR} STREQUAL Ninja)
    add_custom_command(
      OUTPUT ${manifest_path}
      COMMAND true
      DEPENDS deb-chkmanifest-${name}
      COMMENT "Stubbing source manifest for ${name}")
  endif()

  # Glob the common/debian and exports/${name}/debian directories to get a list
  # of files that go in the debian/ directory of the tarball
  add_custom_target(
    deb-chkdebfiles-${name}
    COMMAND
      python -B ${TANGENT_TOOLING}/debhelp.py #
      --outpath ${debfiles_path} #
      check-manifest --patterns common/debian/* exports/${name}/debian/* --
      ${CMAKE_CURRENT_SOURCE_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    BYPRODUCTS ${debfiles_path}
    COMMENT "Checking debian files manifest for ${name}")

  if(NOT ${CMAKE_GENERATOR} STREQUAL Ninja)
    add_custom_command(
      OUTPUT ${debfiles_path}
      COMMAND true
      DEPENDS deb-chkdebfiles-${name}
      COMMENT "Stubbing debian files manifest for ${name}")
  endif()

  # Create the source tarball. We do this just once and then simlink it into the
  # different distribution directoreies.
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${basename}.orig.tar.gz
    COMMAND
      tar --create --gzip #
      --file=${CMAKE_CURRENT_BINARY_DIR}/${basename}.orig.tar.gz #
      --transform 's,^,${basename}/,' #
      --directory ${CMAKE_CURRENT_SOURCE_DIR}/common . #
      --directory ${CMAKE_CURRENT_SOURCE_DIR}/exports/${name} . #
      --directory ${CMAKE_SOURCE_DIR} --files-from ${manifest_path}
    DEPENDS ${manifest_path} ${debfiles_path}
    COMMENT "Creating source tarball ${basename}.orig.tar.gz"
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
  IMPORTVARS(DIRECTORY VARS ${name}_package ${name}_version ${name}_debversion)
  set(basename ${${name}_package}_${${name}_version})
  set(outdir ${CMAKE_CURRENT_BINARY_DIR}/${distro})
  set(changelog ${CMAKE_CURRENT_SOURCE_DIR}/exports/${name}/debian/changelog)

  # Create a symlink to the upstream tarball within the distro-specific working
  # directory
  add_custom_command(
    OUTPUT ${outdir}/${basename}.orig.tar.gz
    COMMAND ${CMAKE_COMMAND} -E make_directory ${outdir}
    COMMAND ${CMAKE_COMMAND} -E create_symlink ../${basename}.orig.tar.gz
            ${outdir}/${basename}.orig.tar.gz
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Creating ${distro} symlink to upstream tarball for ${name}"
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${basename}.orig.tar.gz)

  # These are all the files that are created by debuild
  set(outputs
      ${outdir}/${basename}-${${name}_debversion}~${distro}.debian.tar.xz
      ${outdir}/${basename}-${${name}_debversion}~${distro}.dsc
      ${outdir}/${basename}-${${name}_debversion}~${distro}_source.build
      ${outdir}/${basename}-${${name}_debversion}~${distro}_source.buildinfo
      ${outdir}/${basename}-${${name}_debversion}~${distro}_source.changes)

  get_signing_flags(_signflags)

  # Extract the upstream source tarball, translate the changelog, and run
  # debbuild
  add_custom_command(
    OUTPUT ${outputs}
    # This is the directory where the upstream tarball will be extracted. We
    # need to delete it so that we don't have any stale files
    COMMAND rm -rf ${outdir}/${basename}
    COMMAND tar --directory ${outdir} --extract --gzip
            --file=${outdir}/${basename}.orig.tar.gz
    # Copy the changelog to the distro-specific destination and replace the
    # distribution name
    COMMAND
      python -B ${TANGENT_TOOLING}/debhelp.py translate-changelog #
      --src ${changelog} #
      --tgt ${outdir}/${basename}/debian/changelog #
      --distro ${distro}
    COMMAND
      cd ${outdir}/${basename} #
      && debuild -S -d ${_signflags} > ../${basename}.debuild1.log ||
      (cat ../${basename}.debuild1.log && false)
    DEPENDS ${outdir}/${basename}.orig.tar.gz
    COMMENT "Creating ${distro} source package for ${name}"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

  add_custom_target(
    dput-${name}-${distro}
    COMMAND dput ppa:josh-bialkowski/tangent
            ${outdir}/${basename}-${${name}_debversion}~${distro}_source.changes
    DEPENDS ${outputs})

  add_custom_target(deb-src-${name}-${distro} DEPENDS ${outputs})
  add_dependencies(${distro}-source-packages deb-src-${name}-${distro})
endfunction()

# Create debian package repository from the specified list of binary packages
#
# Usage:
# ~~~
# create_debian_depsrepo(<outdir> <distro> <arch> <deps>...)
function(create_debian_depsrepo depsrepo distro arch)
  # Given a list of all the dependant projects, construct a list of all the .deb
  # files that we depend on
  set(deb_depends)
  foreach(deptag ${ARGN})
    get_property(_deblist GLOBAL PROPERTY deblist-${deptag}-${distro}-${arch})
    list(APPEND deb_depends ${_deblist})
  endforeach()

  # Create rules to copy all our dependant .deb files into a single directory
  # which we will bind to the pbuilder chroot as a filesystem debian repository.
  set(repo_debs)
  foreach(deb ${deb_depends})
    get_filename_component(_filename ${deb} NAME)
    # NOTE(josh): we add the deps/ path suffix so that at least one component is
    # in-common with the bindmount location. We'll need this to generate correct
    # file paths in the Packages file.
    set(repo_deb ${depsrepo}/${_filename})
    add_custom_command(
      OUTPUT ${repo_deb}
      COMMAND ${CMAKE_COMMAND} -E copy ${deb} ${repo_deb}
      DEPENDS ${deb})
    list(APPEND repo_debs ${repo_deb})
  endforeach()

  # Create a rule to generate the debian `Packages` file indexing the packages
  # of our filesystem debian repository.
  add_custom_command(
    OUTPUT ${depsrepo}/Packages
    COMMAND dpkg-scanpackages . > Packages
    # NOTE(josh): the following is equivalent. I'm not sure which tool is better
    # to use??
    #
    # COMMAND apt-ftparchive packages . > Packages
    WORKING_DIRECTORY ${depsrepo}
    DEPENDS ${repo_debs}
    COMMENT "Creating depsrepo for ${tag}")
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

  IMPORTVARS(GLOBAL VARS NATIVE_ARCHITECTURE)
  set(outdir ${CMAKE_CURRENT_BINARY_DIR}/${distro})
  set(basename "${${tag}_package}_${${tag}_version}")
  set(version "${${tag}_version}-${${tag}_debversion}~${distro}")

  get_pbuilder_basetgz(_basetgz ${distro} ${arch})

  # This is a directory where we will copy all of the dependant debian packages
  # and construct a local filesystem debian repository.
  set(depsrepo ${CMAKE_CURRENT_BINARY_DIR}/${distro}/${arch}/${tag}-deps)
  create_debian_depsrepo(${depsrepo} ${distro} ${arch} ${_args_DEPS})

  get_signing_flags(_signflags)

  # ${outputs} contains a list of all the files that are generated as part of
  # the binary packages build. It is generated from the `OUTPUTS` keyword
  # argument by prepending the output directory and appending the version and
  # architecture suffixes.
  set(outputs)
  foreach(binpkg ${_args_OUTPUTS})
    set(debname ${binpkg}_${version}_${arch}.deb)
    list(APPEND outputs ${outdir}/${debname})
  endforeach()

  if("${distro}" STREQUAL "${BUILDENV_DISTRIB_CODENAME}" #
     AND "${arch}" STREQUAL "${NATIVE_ARCHITECTURE}"
     AND NOT ${_args_FORCE_PBUILDER}
     AND NOT _args_DEPS)
    add_custom_command(
      OUTPUT ${outputs}
      # NOTE(josh): add the -nc, --no-pre-clean option to reuse the existing
      # build directory for an incremental build.
      COMMAND debuild -b ${_signflags} > ${outdir}/${basename}.debuild2.log ||
              (cat ${outdir}/${basename}.debuild2.log && false)
      WORKING_DIRECTORY ${outdir}/${basename}
      DEPENDS ${outdir}/${basename}.orig.tar.gz
              ${outdir}/${basename}-${${tag}_debversion}~${distro}.dsc
      COMMENT "Creating (native) binary packages for ${tag}")
  else()
    add_custom_command(
      OUTPUT ${outputs}
      COMMAND
        ${_sudo} env DEB_BUILD_OPTIONS="parallel=8" #
        pbuilder build --distribution #
        ${distro} --architecture ${arch} --basetgz ${_basetgz} #
        --buildresult ${CMAKE_CURRENT_BINARY_DIR}/${distro} #
        --hookdir ${CMAKE_CURRENT_SOURCE_DIR}/pbuilder-hooks #
        --bindmounts "${depsrepo}:/var/cache/pbuilder/deps" #
        --loglevel W #
        --logfile ${outdir}/${basename}.pbuild.log #
        ${outdir}/${basename}-${${tag}_debversion}~${distro}.dsc #
        > /dev/null #
        || (cat ${outdir}/${basename}.pbuild.log && false)
      DEPENDS ${outdir}/${basename}.orig.tar.gz
              ${outdir}/${basename}-${${tag}_debversion}~${distro}.dsc
              ${_basetgz} ${depsrepo}/Packages check-pbuilder-rc
      COMMENT "Creating ${distro}/${arch} (pbuilder) binary pkgs for ${tag}")
  endif()

  add_custom_target(debs-${tag}-${distro}-${arch} DEPENDS ${outputs})
  add_dependencies(debs-${distro}-${arch} debs-${tag}-${distro}-${arch})
  set_property(GLOBAL PROPERTY deblist-${tag}-${distro}-${arch} ${outputs})
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
  set(changelog ${CMAKE_CURRENT_SOURCE_DIR}/exports/${tag}/debian/changelog)
  debhelp_parsechangelog(${changelog} ${tag})
  create_debian_tarball(${tag})

  IMPORTVARS(DIRECTORY VARS ${tag}_package ${tag}_version ${tag}_debversion)

  foreach(distro ${SUPPORTED_DISTRIBUTIONS})
    create_debian_source_package(${tag} ${distro})
    foreach(arch ${SUPPORTED_ARCHITECTURES})
      create_debian_binary_packages(${tag} ${distro} ${arch} ${ARGN})
    endforeach()
  endforeach()
endfunction()

foreach(distro ${SUPPORTED_DISTRIBUTIONS})
  foreach(arch ${SUPPORTED_ARCHITECTURES})
    pbuilder_create(${distro} ${arch})
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
  set(deb_depends)
  foreach(slug tangent-util json argue linkhash)
    get_property(deblist GLOBAL PROPERTY deblist-${slug}-${distro}-${arch})
    list(APPEND deb_depends ${deblist})
  endforeach()
  set(${outvar}
      ${deb_depends}
      PARENT_SCOPE)
endfunction()
