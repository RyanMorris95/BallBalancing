import sys

from PyQt4 import QtCore, QtGui
from ball_balancing_gui import BallBalancingGui


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    print ("here")
    app = QtGui.QApplication.instance()
    print (app)
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        print("QApplication isntance alread exists.")

    print ("HERE")
    window = BallBalancingGui()

    app.setStyle(QtGui.QStyleFactory.create("plastique"))
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    pal.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    pal.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
    pal.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
    pal.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    pal.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    pal.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    pal.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(144, 216, 255).darker())
    app.setPalette(pal)
    app.setStyleSheet("QSeparator { foreground-color: white }")

    print ("here")
    window.show()
    window.run()
    app.aboutToQuit.connect(window.exit_handler)
    sys.exit(app.exec_())


if __name__ == '__main__':
    print ("here")
    main()

