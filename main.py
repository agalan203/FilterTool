from src.mainwindow import *
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    window.show()
    app.exec_()

    #para multiples filtros ver FilterToolApp.py linea 110

    #para multiples filtros: la Plantilla debe ser igual! y cambiar el color de polos y ceros
