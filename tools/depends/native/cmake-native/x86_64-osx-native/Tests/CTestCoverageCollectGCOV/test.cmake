cmake_minimum_required(VERSION 2.8.12)
set(CTEST_PROJECT_NAME "TestProject")
set(CTEST_SOURCE_DIRECTORY "/Users/osx/Desktop/kodi/xbmc/tools/depends/native/cmake-native/x86_64-osx-native/Tests/CTestCoverageCollectGCOV/TestProject")
set(CTEST_BINARY_DIRECTORY "/Users/osx/Desktop/kodi/xbmc/tools/depends/native/cmake-native/x86_64-osx-native/Tests/CTestCoverageCollectGCOV/TestProject")
set(CTEST_CMAKE_GENERATOR "Unix Makefiles")

ctest_empty_binary_directory(${CTEST_BINARY_DIRECTORY})

ctest_start(Experimental)
ctest_configure()
ctest_build()
ctest_test()

list(APPEND CTEST_CUSTOM_COVERAGE_EXCLUDE
	"/foo/something"
	"/3rdparty/"
	"/bar/somethingelse"
)

include(CTestCoverageCollectGCOV)
set(tar_file ${CTEST_BINARY_DIRECTORY}/gcov.tar)
ctest_coverage_collect_gcov(
  TARBALL "${tar_file}"
  SOURCE "${CTEST_SOURCE_DIRECTORY}"
  BUILD "${CTEST_BINARY_DIRECTORY}"
  GCOV_COMMAND "${CMAKE_COMMAND}"
  GCOV_OPTIONS -P "/Users/osx/Desktop/kodi/xbmc/tools/depends/native/cmake-native/x86_64-osx-native/Tests/CTestCoverageCollectGCOV/fakegcov.cmake")

execute_process(COMMAND
  ${CMAKE_COMMAND} -E tar tf ${tar_file}
  OUTPUT_VARIABLE out
  WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

string(REPLACE "\n" ";" out "${out}")
list(SORT out)

set(expected_out
  CMakeFiles/myexecutable.dir/Labels.json
  Testing/CoverageInfo/data.json
  Testing/CoverageInfo/extra.cpp.gcov
  Testing/CoverageInfo/main.cpp.gcov
)

if("${out}" STREQUAL "${expected_out}")
  message("PASSED with correct output: ${out}")
else()
  message(FATAL_ERROR "FAILED: expected:\n${expected_out}\nGot:\n${out}")
endif()
