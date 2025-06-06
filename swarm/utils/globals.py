#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from typing import Optional

class Singleton:
    _instance = None

    @classmethod
    def instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    def reset(self):
        self.value = 0.0

class Cost(Singleton):
    def __init__(self):
        self.value = 0.0

class PromptTokens(Singleton):
    def __init__(self):
        self.value = 0.0

class CompletionTokens(Singleton):
    def __init__(self):
        self.value = 0.0

class Time(Singleton):
    def __init__(self):
        self.value = ""

class Mode(Singleton):
    def __init__(self):
        self.value = ""

class UsageStatisticsObject(Singleton):
    def __init__(self, usage_statistics):
        self.value = usage_statistics