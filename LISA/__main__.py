#! /usr/bin/env python
# -*- coding:Utf8 -*-

import sys
import numpy as np
import OGLWidget as og
import Figure as f

from PyQt5 import Qt
from PyQt5 import QtGui as qg
from OpenGL import GL
from OpenGL.arrays import numpymodule

numpymodule.NumpyHandler.ERROR_ON_COPY = True


class TestOGL(object):

    def __init__(self, *args, **kwargs):
        rand = np.random.rand(100000, 3)
        self._color = np.random.rand(100000, 3).flatten()

        r = rand[:, 0] ** (1. / 3.)
        thet = np.arccos(2 * rand[:, 1] - 1)
        phi = 2. * np.pi * rand[:, 2]

        self._pos = np.array(
            [
                r * np.cos(phi) * np.sin(thet),
                r * np.sin(phi) * np.sin(thet),
                r * np.cos(thet)
            ]
        ).T.flatten()

    def createShaders(self, parent):

        self._shaders = qg.QOpenGLShaderProgram(parent)

        self._shaders.removeAllShaders()
        self._shaders.addShaderFromSourceFile(
            qg.QOpenGLShader.Vertex,   "Shaders/couleurs.vsh")
        self._shaders.addShaderFromSourceFile(
            qg.QOpenGLShader.Fragment, "Shaders/couleurs.fsh")

        if not self._shaders.link():
            raise ShadersNotLinked(
                "Linking shaders in OGLWidget.initialiseGL has failed! " +
                self._shaders.log()
            )

    def show(self, matrice):

        self._shaders.bind()
        self._shaders.setUniformValue("modelview", matrice)

        vertex_id = self._shaders.attributeLocation("in_Vertex")
        color_id = self._shaders.attributeLocation("in_Color")

        self._shaders.enableAttributeArray("in_Vertex")
        self._shaders.enableAttributeArray("in_Color")

        GL.glVertexAttribPointer(
            vertex_id,
            3,
            GL.GL_DOUBLE,
            GL.GL_FALSE,
            0,
            self._pos
        )
        GL.glVertexAttribPointer(
            color_id,
            3,
            GL.GL_DOUBLE,
            GL.GL_FALSE,
            0,
            self._color
        )

        GL.glDrawArrays(GL.GL_POINTS, 0, self._pos.shape[0] // 3)

        self._shaders.disableAttributeArray("in_Vertex")
        self._shaders.disableAttributeArray("in_Color")

        self._shaders.release()

    def createWidget(self, title="Dialogue de test.", parent=None):
        dialog = Qt.QDialog(parent=parent)
        dialog.setWindowOpacity(0.4)
        dialog.setWindowTitle(title)
        dialog.setLayout(Qt.QVBoxLayout())
        dialog.layout().addWidget(
            Qt.QLabel("Ceci est un test d'affichage des widgets.")
        )
        dialog.layout().addWidget(
            Qt.QLabel("Ceci est un test d'affichage des widgets.")
        )
        but = Qt.QPushButton()
        but.setText("Un bouton !")
        but.clicked.connect(self._push_button)
        dialog.layout().addWidget(but)

        return dialog

    def _push_button(self):
        pass


def testOGLWidget():
    app = Qt.QApplication(sys.argv)

    aff = og.OGLWidget()
    for i in range(3):
        aff.lines = TestOGL()
    aff.show()

    return app.exec_()


def testFigure():
    app = Qt.QApplication(sys.argv)

    fig = f.Figure()
    fig.axes = TestOGL()
    fig.show()

    return app.exec_()


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)

    fig = f.Figure()
    fig.axes = TestOGL()
    fig.show()

    sys.exit(app.exec_())
