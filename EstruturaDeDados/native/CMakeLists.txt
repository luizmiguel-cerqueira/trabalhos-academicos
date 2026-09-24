cmake_minimum_required(VERSION 3.20)

project(datastructures LANGUAGES C)

add_library(datastructures SHARED src/ds_api_all.c)

target_compile_features(datastructures PRIVATE c_std_11)
target_include_directories(datastructures PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
set_target_properties(datastructures PROPERTIES
    PREFIX ""
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin/x64"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin/x64"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin/x64"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
