cmake_minimum_required(VERSION 2.8)

# Settings:
set(CTEST_DASHBOARD_ROOT                "/Users/osx/Desktop/kodi/xbmc/tools/depends/native/cmake-native/x86_64-osx-native/Tests/CTestTest")
set(CTEST_SITE                          "Aruns-Mac.local")
set(CTEST_BUILD_NAME                    "CTestTest-Darwin-g++-ConfigFileInBuildDir2")

set(CTEST_SOURCE_DIRECTORY              "/Users/osx/Desktop/kodi/xbmc/tools/depends/native/cmake-native/x86_64-osx-native/Tests/CTestTestConfigFileInBuildDir")
set(CTEST_BINARY_DIRECTORY              "/Users/osx/Desktop/kodi/xbmc/tools/depends/native/cmake-native/x86_64-osx-native/Tests/CTestTestConfigFileInBuildDir2")
set(CTEST_CVS_COMMAND                   "CVSCOMMAND-NOTFOUND")
set(CTEST_CMAKE_GENERATOR               "Unix Makefiles")
set(CTEST_CMAKE_GENERATOR_PLATFORM      "")
set(CTEST_CMAKE_GENERATOR_TOOLSET       "")
set(CTEST_BUILD_CONFIGURATION           "$ENV{CMAKE_CONFIG_TYPE}")
set(CTEST_COVERAGE_COMMAND              "/usr/bin/gcov")
set(CTEST_NOTES_FILES                   "${CTEST_SCRIPT_DIRECTORY}/${CTEST_SCRIPT_NAME}")

CTEST_START(Experimental)
CTEST_CONFIGURE(BUILD "${CTEST_BINARY_DIRECTORY}" RETURN_VALUE res)