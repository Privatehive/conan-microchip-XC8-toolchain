#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
import json, os

required_conan_version = ">=2.0"


class MicrochipXC8ToolchainConan(ConanFile):

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = []
    # ---Sources---
    exports = ["info.json"]
    exports_sources = ["cmake/xc8-*.cmake"]
    # ---Binary model---
    package_type = "application"
    settings = "os", "arch"
    # ---Build---
    generators = []
    # ---Folders---
    no_copy_source = True

    def validate(self):
        valid_os = ["Linux"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

    def source(self):
        # Since v4.00 Microchip provides the compiler as a plain tarball in addition to the .run installer
        get(self, **self.conan_data["sources"][self.version], destination="xc8", strip_root=True)

    def package(self):
        xc8 = os.path.join(self.source_folder, "xc8")
        copy(self, "*", src=xc8, dst=self.package_folder)
        for license_file in ["license.txt", "MPLAB_XC8_C_Compiler_License.rtf", "LLVM_LICENSE.txt", "COPYRIGHT-MUSL.txt"]:
            copy(self, license_file, src=os.path.join(xc8, "docs"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "xc8-*.cmake", src=os.path.join(self.source_folder, "cmake"),
             dst=os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]

        cmake_toolchain = os.path.join(self.package_folder, "cmake", "xc8-toolchain.cmake")
        self.output.info(f"Injecting cmaketoolchain:user_toolchain: {cmake_toolchain}")
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", cmake_toolchain)

        self.buildenv_info.define_path("XC8_ROOT", self.package_folder)
