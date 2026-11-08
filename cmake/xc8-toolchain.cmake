# CMake toolchain file for the Microchip MPLAB XC8 C compiler (PIC targets).
#
# Required variables, set them before project() or pass them as cache variables:
#   XC8_MCU  Target device as accepted by -mcpu, e.g. 16LF1509
#   XC8_DFP  Path to the "xc8" folder of an unpacked Device Family Pack (DFP), e.g.
#            <unpacked Microchip.PIC12-16F1xxx_DFP.1.8.254.atpack>/xc8
#            Since XC8 v3.00 the compiler ships no device support of its own, so a DFP is mandatory.
#            DFPs are available at https://packs.download.microchip.com/
#
# Optimization and debug flags are derived from CMAKE_BUILD_TYPE (see xc8-overrides.cmake).

include_guard()

get_filename_component(XC8_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

set(CMAKE_SYSTEM_NAME Generic)

set(CMAKE_C_COMPILER "${XC8_ROOT}/bin/xc8-cc" CACHE FILEPATH "Path to the compiler binary")
set(CMAKE_ASM_COMPILER "${XC8_ROOT}/bin/xc8-cc" CACHE FILEPATH "Path to the compiler binary")
set(CMAKE_AR "${XC8_ROOT}/bin/xc8-ar" CACHE FILEPATH "Path to the archiver binary")
set(CMAKE_OBJDUMP "${XC8_ROOT}/bin/pic-objdump" CACHE FILEPATH "Path to the objdump binary")
set(CMAKE_RANLIB "" CACHE FILEPATH "XC8 has no ranlib")

# xc8-cc can't build anything without a device, so skip the compiler checks and ABI detection
set(CMAKE_C_COMPILER_WORKS YES CACHE BOOL "The compiler works, but can't be run during the configuration stage")
set(CMAKE_ASM_COMPILER_WORKS YES CACHE BOOL "The assembler works, but can't be run during the configuration stage")
set(CMAKE_C_ABI_COMPILED YES)
set(CMAKE_ASM_ABI_COMPILED YES)

# Rules that must be applied after CMake's own compiler/platform modules
set(CMAKE_USER_MAKE_RULES_OVERRIDE "${CMAKE_CURRENT_LIST_DIR}/xc8-overrides.cmake")

if(NOT XC8_MCU)
    message(FATAL_ERROR "XC8: Set XC8_MCU to the target device (e.g. set(XC8_MCU 16LF1509) before project())")
endif()
if(NOT XC8_DFP)
    message(FATAL_ERROR "XC8: Set XC8_DFP to the 'xc8' folder of the Device Family Pack (DFP) for ${XC8_MCU}")
endif()
if(NOT IS_DIRECTORY "${XC8_DFP}")
    message(FATAL_ERROR "XC8: XC8_DFP does not point to a directory: ${XC8_DFP}")
endif()
list(APPEND CMAKE_TRY_COMPILE_PLATFORM_VARIABLES XC8_MCU XC8_DFP)

# The link step runs the compiler driver with <FLAGS>, so the device also reaches the linker
string(APPEND CMAKE_C_FLAGS_INIT " -mcpu=${XC8_MCU} -mdfp=${XC8_DFP}")
string(APPEND CMAKE_ASM_FLAGS_INIT " -mcpu=${XC8_MCU} -mdfp=${XC8_DFP}")

# IDE support: CLion custom compiler definition (see xc8-clion.cmake)
if(NOT CMAKE_IN_TRY_COMPILE)
    include("${CMAKE_CURRENT_LIST_DIR}/xc8-clion.cmake")
endif()
