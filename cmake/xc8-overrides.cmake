# Included via CMAKE_USER_MAKE_RULES_OVERRIDE (see xc8-toolchain.cmake) after CMake's built-in
# compiler and platform modules, so these settings take precedence.

# XC8 (PIC) compiles C sources to p-code files
set(CMAKE_C_OUTPUT_EXTENSION .p1)
set(CMAKE_ASM_OUTPUT_EXTENSION .o)

set(CMAKE_DEPFILE_FLAGS_C "-MD -MF <DEP_FILE>")
set(CMAKE_DEPFILE_FLAGS_ASM "-MD -MF <DEP_FILE>")

set(CMAKE_C_ARCHIVE_CREATE "<CMAKE_AR> <LINK_FLAGS> <TARGET> <OBJECTS>")
set(CMAKE_ASM_CREATE_STATIC_LIBRARY "<CMAKE_AR> <LINK_FLAGS> <TARGET> <OBJECTS>")

# Since XC8 v4.00 all optimization levels are available without a license
foreach(lang C ASM)
    set(CMAKE_${lang}_FLAGS_DEBUG_INIT "-O0 -gdwarf-3")
    set(CMAKE_${lang}_FLAGS_RELEASE_INIT "-O2")
    set(CMAKE_${lang}_FLAGS_RELWITHDEBINFO_INIT "-O2 -gdwarf-3")
    set(CMAKE_${lang}_FLAGS_MINSIZEREL_INIT "-Os")
endforeach()
