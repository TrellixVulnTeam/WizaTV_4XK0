SET(APP_NAME Kodi)
SET(APP_NAME_LC kodi)
SET(APP_NAME_UC KODI)
SET(APP_VERSION_MAJOR 16)
SET(APP_VERSION_MINOR 1)
IF(NOT KODI_PREFIX)
  SET(KODI_PREFIX /Users/Shared/xbmc-depends/iphoneos9.2_armv7-target)
ENDIF()
IF(NOT KODI_INCLUDE_DIR)
  SET(KODI_INCLUDE_DIR /Users/Shared/xbmc-depends/iphoneos9.2_armv7-target/include/kodi)
ENDIF()
IF(NOT KODI_LIB_DIR)
  SET(KODI_LIB_DIR /Users/Shared/xbmc-depends/iphoneos9.2_armv7-target/lib/kodi)
ENDIF()
IF(NOT WIN32)
  SET(CMAKE_CXX_FLAGS "$ENV{CXXFLAGS} ")
ENDIF()
LIST(APPEND CMAKE_MODULE_PATH /Users/Shared/xbmc-depends/iphoneos9.2_armv7-target/lib/kodi)
ADD_DEFINITIONS(-DTARGET_POSIX -DTARGET_DARWIN -DTARGET_DARWIN_IOS -D_LINUX -DBUILD_KODI_ADDON)

if(NOT CORE_SYSTEM_NAME)
  if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(CORE_SYSTEM_NAME "osx")
  else()
    string(TOLOWER ${CMAKE_SYSTEM_NAME} CORE_SYSTEM_NAME)
  endif()
endif()

include(addon-helpers)
