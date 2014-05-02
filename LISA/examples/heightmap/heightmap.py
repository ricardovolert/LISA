#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
# import sip
import datetime

# from PyQt5.QtGui import *
# from PyQt4.QtOpenGL import QGLShaderProgram as QOpenGLShaderProgram
# from PyQt4.QtOpenGL import QGLBuffer as QOpenGLBuffer
# from PyQt4.QtOpenGL import QGLShader as QOpenGLShader
from OpenGL import GL
from OpenGL.arrays import numpymodule
from scipy.misc import imread

from LISA import Shaders as s
from LISA import common as c
from LISA import Buffers as buf

numpymodule.NumpyHandler.ERROR_ON_COPY = True


class ShadersNotLinked(Exception):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class HeightMap(object):

    def __init__(self, *args, **kwargs):

        # create mesh
        self.npoints = 80
        X = np.linspace(-1, 1, self.npoints)
        Y = np.linspace(-1, 1, self.npoints)
        Z = np.zeros(self.npoints, dtype=np.float32)
        x, y, z = np.meshgrid(X, Y, Z)
        self._mesh = np.array([x, y, z], dtype=np.float32).T.flatten()

        # create the indices for triangles
        self._indices = np.empty(
            (self.npoints - 1, self.npoints - 1, 6),
            dtype=np.uint32
        )
        indices = np.array(range(self.npoints - 1), dtype=np.uint32)
        for i in range(self.npoints - 1):
            self._indices[i, :, 0] = indices[:] + i * self.npoints
            self._indices[i, :, 1] = indices[:] + 1 + i * self.npoints
            self._indices[i, :, 2] = indices[:] + (i + 1) * self.npoints
            self._indices[i, :, 3] = indices[:] + (i + 1) * self.npoints
            self._indices[i, :, 4] = indices[:] + 1 + (i + 1) * self.npoints
            self._indices[i, :, 5] = indices[:] + 1 + i * self.npoints
        self._indices = self._indices.flatten()

        self._time = datetime.datetime.now()

    def createShaders(self, parent):

        self._shaders = s.CreateShaderFromFile(
            c.os.path.join(
                c.SHADERS_DIR,
                "heightmap/heightmap.vsh"
            )
        ) + s.CreateShaderFromFile(
            c.os.path.join(
                c.SHADERS_DIR,
                "heightmap/heightmap.fsh"
            )
        )

        self._texture = GL.glGenTextures(1)
        im = imread(
            c.os.path.join(
                c.TEXTURE_DIR,
                "heightmap/two.png"
            )
        )
        im.astype(np.int8)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D,
            GL.GL_TEXTURE_MIN_FILTER,
            GL.GL_LINEAR,
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D,
            GL.GL_TEXTURE_MAG_FILTER,
            GL.GL_LINEAR,
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D,
            GL.GL_TEXTURE_WRAP_S,
            GL.GL_CLAMP,
        )
        GL.glTexParameteri(
            GL.GL_TEXTURE_2D,
            GL.GL_TEXTURE_WRAP_T,
            GL.GL_CLAMP,
        )
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            3,
            im.shape[0],
            im.shape[1],
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            im,
        )

        self._shaders.link()

        # create buffers
        self._vertices = buf.Buffer(buf.VERTEX_BUFFER)
        self._index = buf.Buffer(buf.INDEX_BUFFER)
        self._vertices.create()
        self._index.create()

        # allocate buffers
        self._vertices.bind()
        self._vertices.allocate(
            self._mesh,
            len(self._mesh) * 4
        )
        self._vertices.release()
        self._index.bind()
        self._index.allocate(
            self._indices,
            len(self._indices) * 4
        )
        self._index.release()

    def show(self, parent):
        self._shaders.bind()
        mat = parent._projection * parent._view * parent._model
        self._shaders.setUniformValue(
            "modelview",
            mat,
        )

        # to use the vertex buffer
        self._vertices.bind()

        # get the location and enabsle the attribute array
        self._shaders.enableAttributeArray("in_Vertex")

        # send data from buffer
        self._shaders.setAttributeBuffer(
            "in_Vertex",
            self._mesh,
        )

        # make available the vertex buffer again
        self._vertices.release()

        # use the index buffer
        self._index.bind()

        # use it to draw where the indices are taken from the binded buffer
        # to draw the mesh
        GL.glDrawElements(
            GL.GL_TRIANGLES,
            6 * (self.npoints - 1) ** 2,
            GL.GL_UNSIGNED_INT,
            None,
        )

        # make available the buffer again
        self._index.release()

        # realeas all
        self._shaders.disableAttributeArray("in_Vertex")
        self._shaders.release()


# vim: set tw=79 :
