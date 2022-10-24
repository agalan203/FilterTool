from src.mainwindow import *
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    window.show()
    app.exec_()

    #maybe agrega lo de las imagenes de la plantilla de cada filtro
    #arreglar lo de las stages
    #ver pq tarda tanto 
