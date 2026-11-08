#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        self.run("xc8-cc --version", env="conanbuild")
