cmake_minimum_required(VERSION 3.4)

find_package(PkgConfig REQUIRED)
pkg_search_module(GLIB REQUIRED glib-2.0)
pkg_search_module(MBIM REQUIRED mbim-glib)
pkg_search_module(QMI REQUIRED qmi-glib)
pkg_search_module(JSON-C REQUIRED json-c)

include_directories(${GLIB_INCLUDE_DIRS})
include_directories(${QMI_INCLUDE_DIRS})
include_directories(${JSON-C_INCLUDE_DIRS})
include_directories(../include)

add_executable(it2s-data-reader it2s-data-reader.cpp qmi.cpp)
target_link_libraries(it2s-data-reader ${GLIB_LDFLAGS} ${QMI_LDFLAGS} ${JSON-C_LDFLAGS} it2s_gnss mosquitto pthread rt)
#target_link_libraries(it2s-data-reader ${GLIB_LDFLAGS} ${QMI_LDFLAGS} -lit2s-config-etsi-its it2s-asn-misc-vsm it2s-asn-etsi-its-v1-cdd-1.3.1 it2s-peripherals it2s_gnss it2s-peripherals mosquitto pthread rt)
install(TARGETS it2s-data-reader RUNTIME DESTINATION bin COMPONENT it2s-data-reader)
