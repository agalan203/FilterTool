from src.mainwindow import *
#TODO Ojo retardo de grupo que el w todavia esta pq no lo entiendo
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    window.show()
    app.exec_()