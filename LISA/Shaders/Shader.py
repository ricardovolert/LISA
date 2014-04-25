#!/usr/bin/env python
# encoding: utf-8

from OpenGL import GL
from . import ShaderProgram as s


VERTEX_SHADER = GL.GL_VERTEX_SHADER
FRAGMENT_SHADER = GL.GL_FRAGMENT_SHADER


class ShaderCompileError(Exception):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class Shader(object):
    def __init__(self, src, stype):
        self.id = stype
        self.src = src

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, val):
        self._src = val
        GL.glShaderSource(
            self.id,
            val
        )
        GL.glCompileShader(self.id)
        log = GL.glGetShaderInfoLog(self.id)
        if log:
            raise ShaderCompileError(log)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = GL.createShader(
            val
        )

    def _addShader(self, val):
        if isinstance(val, s.ShaderProgram):
            return val + self
        sp = s.ShaderProgram()
        sp += self
        sp += val
        return sp

    def __add__(self, val):
        return self._addShader(val)

    def __radd__(self, val):
        return self._addShader(val)

def CreateShaderFromFile(filename, stype):
    # Read the file:
    with open(filename, "r") as f:
        src = f.readlines()

    # Give it to the Shader class and return the resulting object:
    return Shader(src, stype)
