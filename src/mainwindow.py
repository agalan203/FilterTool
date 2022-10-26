from src.ui.mainwindow3 import *
import numpy as np
from numpy import linspace, logspace, cos, sin, heaviside, log10, floor, zeros, ones, pi, diff, unwrap
import sys
import os
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QWidget, QPushButton, QAction, QLineEdit, \
    QMessageBox, QRadioButton, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap

import scipy.signal as signal

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.designconfiguration import *
from src.approximations import *
from src.filterstage import *
from src.filterdesign import *
from src.Filter import *

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        #Initialization
        self.setWindowTitle("Filter Tool - Grupo 1")
        self.resize(1000, 1000)
        self.tabs_menu.setCurrentIndex(0)
        self.tabPlots.setCurrentIndex(0)
        self.tabPlots_2.setCurrentIndex(0)

        self.filterImagen = [ resource_path("res/lowpasstemplate.png"), resource_path("res/highpasstemplate.png"),
                    resource_path("res/bandpasstemplate.png"), resource_path("res/bandstoptemplate.png"), resource_path("res/groupdelaytemplate.png") ]

        #Updates
        self.updateType(self.filterImagen)
        self.updateAprox()

        #Variables
        self.filters = []
        self.num_plots = self.tabPlots.count()
        self.plot_layouts = [self.plotlayout_1, self.plotlayout_2, self.plotlayout_3, self.plotlayout_4,
                             self.plotlayout_5, self.plotlayout_6]
        self.num_plots2 = self.tabPlots_2.count()
        self.plot_layouts2 = [self.plotlayout2_1, self.plotlayout2_2, self.plotlayout2_3]
        
        #Callbacks
        #Save and recall
        self.btn_save.clicked.connect(self.saveFile)
        self.btn_open.clicked.connect(self.openFile)
        self.btn_save_2.clicked.connect(self.exportFile)

        #Filter design
        self.combo_tipo.currentIndexChanged.connect(lambda: self.updateType(self.filterImagen))
        self.combo_aprox.currentIndexChanged.connect(self.updateAprox)
        self.add_filter.clicked.connect(self.addFilter)
        self.remove_filter.clicked.connect(self.removeFilter)
        self.filters_list.itemChanged.connect(self.onFilterItemChanged)
        self.filters_list.itemDoubleClicked.connect(self.writeOrden)
        self.check_plantilla_GD.stateChanged.connect(self.plotAll)

        #Stage design
        self.btn_new_stage.clicked.connect(self.newStage)
        self.btn_edit_stage.clicked.connect(self.editStage)
        self.btn_plot_stage.clicked.connect(self.plotStage)
        self.btn_delete_stage.clicked.connect(self.deleteStage)
        self.stage_list.itemClicked.connect(self.updateStageView)
        self.combo_filtro.currentIndexChanged.connect(self.updateStageMenu)

        #Plots
        #Filter design
        self.plot_types = {'Atenuación': 0, 'Fase': 1, 'Retardo de Grupo': 2, 'Polos y Ceros': 3,
                           'Escalón': 4, 'Máximo Q': 5}
        self.plot_types2 = {'Polos y Ceros 2': 0, 'Respuesta Total': 1, 'Respuesta Etapa': 2}
        self.figure = [Figure() for x in range(self.num_plots)]
        self.canvas = [FigureCanvas(self.figure[x]) for x in range(self.num_plots)]
        self.axes = [self.figure[x].subplots() for x in range(self.num_plots)]
        for x, layout in enumerate(self.plot_layouts):
            layout.addWidget(NavigationToolbar(self.canvas[x], self))
            layout.addWidget(self.canvas[x])
            self.figure[x].tight_layout()
            self.axes[x].grid(True, which='both')
            self.axes[x].axhline(linewidth=1, color='k')
            self.axes[x].axvline(linewidth=1, color='k')
            self.axes[x].set_xlabel('Frecuencia [Hz]')

        self.axes[0].set_xscale('log')
        self.axes[1].set_xscale('log')
        self.axes[2].set_xscale('log')
        self.axes[0].set_xlabel('Frecuencia [Hz]')
        self.axes[1].set_xlabel('Frecuencia [Hz]')
        self.axes[2].set_xlabel('Frecuencia [Hz]')
        self.axes[3].set_xlabel('σ')
        self.axes[4].set_xlabel('t [s]')
        self.axes[5].set_xlabel('σ')

        self.axes[0].set_ylabel('Atenuación [dB]')
        self.axes[1].set_ylabel('Fase [°]')
        self.axes[2].set_ylabel('Retardo de grupo [s]')
        self.axes[3].set_ylabel('jω')
        self.axes[4].set_ylabel('Tensión [V]')
        self.axes[5].set_ylabel('jω')

        #Stage Design
        self.figure2 = [Figure() for x in range(self.num_plots2)]
        self.canvas2 = [FigureCanvas(self.figure2[x]) for x in range(self.num_plots2)]
        self.axes2 = [self.figure2[x].subplots() for x in range(self.num_plots2)]
        for x, layout in enumerate(self.plot_layouts2):
            layout.addWidget(NavigationToolbar(self.canvas2[x], self))
            layout.addWidget(self.canvas2[x])
            self.figure2[x].tight_layout()
            self.axes2[x].grid(True, which='both')
            self.axes2[x].axhline(linewidth=1, color='k')
            self.axes2[x].axvline(linewidth=1, color='k')

        self.axes2[0].set_xlabel('σ')
        self.axes2[1].set_xlabel('Frecuencia [Hz]')
        self.axes2[2].set_xlabel('Frecuencia [Hz]')
        self.axes2[0].set_ylabel('jω')
        self.axes2[1].set_ylabel('Amplitud [dB]')
        self.axes2[2].set_ylabel('Amplitud [dB]')

    #Functions
    def saveFile(self):
        selected = self.filters_list.selectedItems()
        if len(selected) > 0:
            index = self.filters_list.row(selected[0])
            self.filters[index].filter_design.setFilterStages(self.filters[index].filter_stages)
            filename = QFileDialog.getSaveFileName(self, "Guardar Archivo", "filtro.ft", "Filter Tool (*.ft)", "Filter Tool (*.ft)")[0]
            if len(filename) > 0:
                try:
                    self.filters[index].filter_design.save(filename)
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("Error guardando el archivo")
                    msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia")
            msg.setText("Seleccionar un filtro para guardar.")
            msg.exec_()
            return False
        return

    def openFile(self):
        msgbox = QMessageBox(QMessageBox.Question, "Confirmación", "¿Quiere abrir un archivo?\nSe perderá el progreso actual.")
        msgbox.addButton(QMessageBox.Yes)
        msgbox.addButton(QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.No)
        reply = msgbox.exec()
        if reply == QMessageBox.Yes:
            filename = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Filter Tool (*.ft)", "Filter Tool (*.ft)")[0]
            if filename:
                try:
                    name = os.path.splitext(os.path.basename(filename))[0]
                    self.lineEdit.setText(name)
                    self.filters.append(Filter())
                    self.filters[len(self.filters)-1].filter_design.open(filename)
                    self.filters[len(self.filters)-1].designconfig = self.filters[len(self.filters)-1].filter_design.dc
                    self.combo_tipo.setCurrentIndex(self.filters[len(self.filters)-1].designconfig.type)
                    self.combo_aprox.setCurrentIndex(self.filters[len(self.filters)-1].designconfig.aprox_types.index(self.filters[len(self.filters)-1].designconfig.aprox))
                    self.spin_denorm.setValue(self.filters[len(self.filters)-1].designconfig.denorm)
                    self.spin_minord.setValue(self.filters[len(self.filters)-1].designconfig.minord)
                    self.spin_maxord.setValue(self.filters[len(self.filters)-1].designconfig.maxord)
                    self.spin_qmax.setValue(self.filters[len(self.filters)-1].designconfig.qmax)
                    self.spin_Ap.setValue(self.filters[len(self.filters)-1].designconfig.Ap)
                    self.spin_ripple.setValue(self.filters[len(self.filters)-1].designconfig.ripple)
                    self.spin_Aa.setValue(self.filters[len(self.filters)-1].designconfig.Aa)
                    self.spin_wp.setValue(self.filters[len(self.filters)-1].designconfig.wp / (2*pi))
                    self.spin_wa.setValue(self.filters[len(self.filters)-1].designconfig.wa / (2*pi))
                    self.spin_wp_2.setValue(self.filters[len(self.filters)-1].designconfig.wp2 / (2*pi))
                    self.spin_wa_2.setValue(self.filters[len(self.filters)-1].designconfig.wa2 / (2*pi))
                    self.GD_tau.setValue(self.filters[len(self.filters)-1].designconfig.tau)
                    self.GD_wrg.setValue(self.filters[len(self.filters)-1].designconfig.wrg / (2*pi))
                    self.GD_gamma.setValue(self.filters[len(self.filters)-1].designconfig.gamma)

                    self.updateFilterList()
                    self.plotAll()

                    self.filters[len(self.filters)-1].gain_remaining = self.filters[len(self.filters)-1].filter_design.gain

                    self.filters[len(self.filters)-1].filter_stages = self.filters[len(self.filters)-1].filter_design.stages
                    self.stage_list.clear()
                    for label, stage in self.filters[len(self.filters)-1].filter_stages.items():
                        self.filters[len(self.filters)-1].gain_remaining -= stage.gain
                        self.stage_list.addItem(label)
                        self.combo_polo1.model().item(stage.pole1 + 1).setEnabled(False)
                        self.combo_polo2.model().item(stage.pole1 + 1).setEnabled(False)
                        self.combo_polo1.model().item(stage.pole2 + 1).setEnabled(False)
                        self.combo_polo2.model().item(stage.pole2 + 1).setEnabled(False)
                        self.combo_cero1.model().item(stage.zero1 + 1).setEnabled(False)
                        self.combo_cero2.model().item(stage.zero1 + 1).setEnabled(False)
                        self.combo_cero1.model().item(stage.zero2 + 1).setEnabled(False)
                        self.combo_cero2.model().item(stage.zero2 + 1).setEnabled(False)
                    self.label_gain_total.setText('Restante: {:.3f} dB'.format(self.filters[len(self.filters)-1].gain_remaining))
                except:
                    self.filters.pop(len(self.filters)-1)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("Error abriendo el archivo")
                    msg.exec_()
                return True
        return False

    def exportFile(self):
        selection = self.filters_list.selectedItems()
        if len(selection) > 0:
            index = self.filters_list.row(selection[0])
            
            filename = QFileDialog.getSaveFileName(self, "Exportar Archivo", "filtro.pdf", "PDF (*.pdf)", "PDF (*.pdf)")[0]
            if len(filename) > 0:
                try:
                    self.filters[index].filter_design.export(filename)
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("Error exportando el archivo")
                    msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia")
            msg.setText("Seleccionar un filtro para exportar.")
            msg.exec_()
            return False
        return

    def set_A_Template(self):
        for i in range(self.combo_aprox.count()):
            self.combo_aprox.model().item(i).setEnabled(i != 5 and i != 6)

        if self.combo_aprox.currentIndex() == 5 or self.combo_aprox.currentIndex() == 6:
            self.combo_aprox.setCurrentIndex(0)

        self.spin_denorm.setEnabled(True)
        self.GD_tau.setEnabled(False)
        self.GD_wrg.setEnabled(False)
        self.GD_gamma.setEnabled(False)

        type = self.combo_tipo.currentText()
        self.spin_Ap.setEnabled(True)
        self.spin_ripple.setEnabled(True)
        self.spin_Aa.setEnabled(True)
        self.spin_wp.setEnabled(True)
        self.spin_wa.setEnabled(True)
        return

    def set_GD_Template(self):
        for i in range(self.combo_aprox.count()):
            self.combo_aprox.model().item(i).setEnabled(i == 5 or i == 6)

        if self.combo_aprox.currentIndex() != 5 and self.combo_aprox.currentIndex() != 6:
            self.combo_aprox.setCurrentIndex(5)

        self.spin_denorm.setEnabled(False)
        self.GD_tau.setEnabled(True)
        self.GD_wrg.setEnabled(True)
        self.GD_gamma.setEnabled(True)
        self.spin_Ap.setEnabled(False)
        self.spin_ripple.setEnabled(False)
        self.spin_Aa.setEnabled(False)
        self.spin_wp.setEnabled(False)
        self.spin_wp_2.setEnabled(False)
        self.spin_wa.setEnabled(False)
        self.spin_wa_2.setEnabled(False)
        return

    def updateType(self, filterImg):
        self.label_imagefilter.setPixmap(QPixmap(filterImg[self.combo_tipo.currentIndex()]))
        type = self.combo_tipo.currentText()
        w_band = (type == 'Pasa Banda') or (type == 'Rechaza Banda')
        g_delay = type == 'Retardo de Grupo'
        if not g_delay:
            self.set_A_Template()
            self.label_wp_2.setEnabled(w_band)
            self.spin_wp_2.setEnabled(w_band)
            self.label_wa_2.setEnabled(w_band)
            self.spin_wa_2.setEnabled(w_band)

            self.label_wp.setText('Frecuencia fp+ [Hz]' if w_band else 'Frecuencia fp [Hz]')
            self.label_wa.setText('Frecuencia fa+ [Hz]' if w_band else 'Frecuencia fa [Hz]')
        else:
            self.set_GD_Template()

        return

    def updateAprox(self):
        return

    def plotAll(self):
        for x, ax in enumerate(self.axes):
            ax.clear()
            ax.grid()
        for x, ax in enumerate(self.axes2):
            ax.clear()
            ax.grid()
        
        for filter in self.filters:
            if (filter.visible == True):
                filter.designconfig.gain = filter.designconfig.ripple - filter.designconfig.Ap
                filter.gain_remaining = filter.designconfig.gain
                self.label_gain_total.setText('Restante: {:.3f} dB'.format(filter.gain_remaining))

                if (self.check_plantilla_GD.isChecked()):
                    self.plotTemplate(filter.designconfig.type, filter.designconfig.Ap, filter.designconfig.ripple, filter.designconfig.Aa, filter.designconfig.wp, filter.designconfig.wa, filter.designconfig.wp2, filter.designconfig.wa2, filter.designconfig.tau, filter.designconfig.gamma, filter.designconfig.wrg) #TYPE ESTA MAL

                # Aproximation
                if filter.designconfig.aprox == 'Butterworth':
                    z, p, k, n = Butterworth(filter.designconfig)
                elif filter.designconfig.aprox == 'Chebyshev I':
                    z, p, k, n = ChebyshevI(filter.designconfig)
                elif filter.designconfig.aprox == 'Chebyshev II':
                    z, p, k, n = ChebyshevII(filter.designconfig)
                elif filter.designconfig.aprox == 'Bessel':
                    z, p, k, n = Bessel(filter.designconfig)
                elif filter.designconfig.aprox == 'Cauer':
                    z, p, k, n = Cauer(filter.designconfig)
                elif filter.designconfig.aprox == 'Gauss':
                    z, p, k, n = Gauss(filter.designconfig)
                elif filter.designconfig.aprox == 'Legendre':
                    z, p, k, n = Legendre(filter.designconfig)

                filter.orden = n

                try:
                    if filter.designconfig.Ap <= 0:
                        k *= 10**(filter.designconfig.gain / 20)
                    filter_system = signal.ZerosPolesGain(z, p, k)
                    # Atenuacion y Fase
                    if filter.designconfig.getType() == 'Pasa Bajos' or filter.designconfig.getType() == 'Pasa Altos':
                        lowerfreq = filter.designconfig.wp / 10
                        higherfreq = filter.designconfig.wa * 10
                    elif filter.designconfig.getType() == 'Pasa Banda' or filter.designconfig.getType() == 'Rechaza Banda':
                        lowerfreq = min(filter.designconfig.wa, filter.designconfig.wp, filter.designconfig.wa2, filter.designconfig.wp2) / 10
                        higherfreq = max(filter.designconfig.wa, filter.designconfig.wp, filter.designconfig.wa2, filter.designconfig.wp2) * 10
                    elif filter.designconfig.aprox == 'Bessel' or filter.designconfig.aprox == 'Gauss':
                        lowerfreq = filter.designconfig.wrg/10
                        higherfreq = filter.designconfig.wrg * 10

                    x = np.logspace((log10(lowerfreq)), (log10(higherfreq)), num=1000)
                    Gain = signal.bode(filter_system, x)
                    Attenuation = signal.bode(signal.ZerosPolesGain(p, z, 1 / k), x)
                    freq = Attenuation[0] / (2* pi)
                    freq1 = Gain[0] / (2* pi)
                    self.getPlotAxes('Atenuación').semilogx(freq, Attenuation[1], label = filter.designconfig.name)
                    self.getPlotAxes('Fase').semilogx(freq1, Gain[2], label = filter.designconfig.name)
                    self.getPlotAxes('Respuesta Total').semilogx(freq1, Gain[1], label = filter.designconfig.name)

                    # Retardo de Grupo
                    w, h = signal.freqs_zpk(z, p, k, x)
                    gd = -np.diff(np.unwrap(np.angle(h))) / np.diff(w)
                    freq = w[1:] / (2* pi)
                    self.getPlotAxes('Retardo de Grupo').semilogx(freq, gd, label = filter.designconfig.name)

                    # Polos y Ceros
                    self.stage_list.clear()
                    self.combo_polo1.clear()
                    self.combo_polo2.clear()
                    self.combo_cero1.clear()
                    self.combo_cero2.clear()
                    self.combo_polo1.addItem('-') 
                    self.combo_polo2.addItem('-')
                    self.combo_cero1.addItem('-')
                    self.combo_cero2.addItem('-')
                    self.plotPolesAndZeros(z, p, filter.designconfig.name)

                    # Respuestas temporales
                    t, y = signal.step(filter_system, N = 1000)
                    self.getPlotAxes('Escalón').plot(t, y, label = filter.designconfig.name)

                    # Máximo Q
                    self.plotQFactor(z, p, filter.designconfig.name)

                    # Guardar Datos
                    filter.filter_design.setDesignConfig(filter.designconfig)
                    filter.filter_design.setPolesAndZeros(p, z)

                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error!")
                    msg.setText("Error generando gráficos")
                    msg.exec_()

        self.axes[0].set_xlabel('Frecuencia [Hz]')
        self.axes[1].set_xlabel('Frecuencia [Hz]')
        self.axes[2].set_xlabel('Frecuencia [Hz]')
        self.axes[3].set_xlabel('σ')
        self.axes[4].set_xlabel('t [s]')
        self.axes[5].set_xlabel('σ')
        self.axes[0].set_ylabel('Atenuación [dB]')
        self.axes[1].set_ylabel('Fase [°]')
        self.axes[2].set_ylabel('Retardo de grupo [s]')
        self.axes[3].set_ylabel('jω')
        self.axes[4].set_ylabel('Tensión [V]')
        self.axes[5].set_ylabel('jω')

        self.axes2[0].set_xlabel('σ')
        self.axes2[1].set_xlabel('Frecuencia [Hz]')
        self.axes2[2].set_xlabel('Frecuencia [Hz]')
        self.axes2[0].set_ylabel('jω')
        self.axes2[1].set_ylabel('Amplitud [dB]')
        self.axes2[2].set_ylabel('Amplitud [dB]')

        for x, canv in enumerate(self.canvas):
            self.axes[x].legend()
            self.figure[x].tight_layout()
            canv.draw()
        for x, canv in enumerate(self.canvas2):
            self.axes2[x].legend()
            self.figure2[x].tight_layout()
            canv.draw()
        
        self.updateStageMenu()
        

    def plotTemplate(self, type, Ap, ripple, Aa, wp, wa, wp2, wa2, tau, gamma, wrg):
        signaltypes = ['Pasa Bajos', 'Pasa Altos', 'Pasa Banda',
                   'Rechaza Banda', 'Retardo de Grupo']
        if signaltypes[type] == 'Pasa Bajos':
            x = [wp / 10 / (2*pi), wp/ (2*pi), wp/ (2*pi)]
            y = [Ap, Ap, Aa + 10]
            if Ap <= 0:
                yR = [Ap-ripple, Ap-ripple]
            else:
                yR = [ripple, ripple]
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].semilogx(x[:-1], yR, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            x = [wa/ (2*pi), wa/ (2*pi), wa * 10/ (2*pi)]
            y = [Ap - 10, Aa, Aa]
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
        elif signaltypes[type] == 'Pasa Altos':
            x = [wa / 10/ (2*pi), wa/ (2*pi), wa/ (2*pi)]
            y = [Aa, Aa, Ap - 10]
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            x = [wp/ (2*pi), wp/ (2*pi), wp * 10/ (2*pi)]
            y = [Aa + 10, Ap, Ap]
            if Ap <= 0:
                yR = [Ap-ripple, Ap-ripple]
            else:
                yR = [ripple, ripple]
            self.axes[0].semilogx(x[1:], yR, '-', color='#1a6125', linewidth=2)
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
        elif signaltypes[type] == 'Pasa Banda':
            w = [[wp,wp2],[wa,wa2]]
            f0 = np.sqrt(w[0][0]*w[0][1])
            f0a = np.sqrt(w[1][0]*w[1][1])
            if f0a > f0:
                x = [f0**2/w[1][1]/ (2*pi), f0**2/w[1][1]/ (2*pi)]
            elif f0a < f0:
                x = [f0**2/w[1][0]/ (2*pi), f0**2/w[1][0]/ (2*pi)]
            y = [Aa, Ap-10]
            self.axes[0].semilogx(x, y, '-', color='#ad1d52', linewidth=2)

            x = [wa2 / 10/ (2*pi), wa2/ (2*pi), wa2/ (2*pi)]
            y = [Aa, Aa, Ap - 10]
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            x = [wp2/ (2*pi), wp2/ (2*pi), wp/ (2*pi), wp/ (2*pi)]
            y = [Aa + 10, Ap, Ap, Aa + 10]
            if Ap <= 0:
                yR = [Ap-ripple, Ap-ripple]
            else:
                yR = [ripple, ripple]
            self.axes[0].semilogx(x[1:-1], yR, '-', color='#1a6125', linewidth=2)
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            x = [wa/ (2*pi), wa/ (2*pi), wa * 10/ (2*pi)]
            y = [Ap - 10, Aa, Aa]
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
        elif signaltypes[type] == 'Rechaza Banda':
            w = [[wp,wp2],[wa,wa2]]
            f0 = np.sqrt(w[0][0]*w[0][1])
            f0a = np.sqrt(w[1][0]*w[1][1])
            if f0a > f0:
                x = [f0**2/w[1][0] / (2*pi), f0**2/w[1][0] / (2*pi)]
            elif f0a < f0:
                x = [f0**2/w[1][1] / (2*pi), f0**2/w[1][1] / (2*pi)]
            y = [Aa, Ap-10]
            self.axes[0].semilogx(x, y, '-', color='#ad1d52', linewidth=2)

            x = [wp2 / 10/ (2*pi), wp2/ (2*pi), wp2/ (2*pi)]
            y = [Ap, Ap, Aa + 10]
            if Ap <= 0:
                yR = [Ap-ripple, Ap-ripple]
            else:
                yR = [ripple, ripple]
            self.axes[0].semilogx(x[:-1], yR, '-', color='#1a6125', linewidth=2)
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            x = [wa2/ (2*pi), wa2/ (2*pi), wa/ (2*pi), wa/ (2*pi)]
            y = [Ap - 10, Aa, Aa, Ap - 10]
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            x = [wp/ (2*pi), wp/ (2*pi), wp * 10/ (2*pi)]
            y = [Aa + 10, Ap, Ap]
            if Ap <= 0:
                yR = [Ap-ripple, Ap-ripple]
            else:
                yR = [ripple, ripple]
            self.axes[0].semilogx(x[1:], yR, '-', color='#1a6125', linewidth=2)
            self.axes[0].semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.axes[0].fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
        elif signaltypes[type] == 'Retardo de Grupo':
            x = [wrg/10/ (2*pi), wrg/ (2*pi), wrg/ (2*pi)]
            y = [tau - (tau * gamma/100), tau - (tau * gamma/100), 0]
            self.getPlotAxes('Retardo de Grupo').semilogx(x, y, '-', color='#1a6125', linewidth=2)
            self.getPlotAxes('Retardo de Grupo').fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)

        return

    def plotPolesAndZeros(self, z, p, name):
        self.getPlotAxes('Polos y Ceros').axhline(linewidth=1, color='k')
        self.getPlotAxes('Polos y Ceros').axvline(linewidth=1, color='k')

        poles_labels = dict()
        zeros_labels = dict()
        for i, pole in enumerate(p):
            self.combo_polo1.addItem('Polo n°' + str(i + 1))
            self.combo_polo2.addItem('Polo n°' + str(i + 1))
            self.getPlotAxes('Polos y Ceros').plot(pole.real, pole.imag, 'rx', markersize=10)
            xy = (pole.real, pole.imag)
            poles_labels[xy] = '{}\n Polo n°'.format(name) + str(i + 1) if xy not in poles_labels else poles_labels[xy] + ', ' + str(i + 1)
        for i, zero in enumerate(z):
            self.combo_cero1.addItem('Cero n°' + str(i + 1))
            self.combo_cero2.addItem('Cero n°' + str(i + 1))
            self.getPlotAxes('Polos y Ceros').plot(zero.real, zero.imag, 'bo', markersize=10, fillstyle='none')
            xy = (zero.real, zero.imag)
            zeros_labels[xy] = '{}\n Cero n°'.format(name) + str(i + 1) if xy not in zeros_labels else zeros_labels[xy] + ', ' + str(i + 1)

        for polexy in poles_labels:
            self.getPlotAxes('Polos y Ceros').annotate(poles_labels[polexy], polexy, textcoords="offset points", xytext=(0, 10), ha='center')
        for zeroxy in zeros_labels:
            self.getPlotAxes('Polos y Ceros').annotate(zeros_labels[zeroxy], zeroxy, textcoords="offset points", xytext = (0, 10), ha = 'center')

        self.getPlotAxes('Polos y Ceros').axis('equal')

        return

    def plotQFactor(self, z, p, name):
        self.getPlotAxes('Máximo Q').axhline(linewidth=1, color='k')
        self.getPlotAxes('Máximo Q').axvline(linewidth=1, color='k')
        self.getPlotAxes('Polos y Ceros 2').axhline(linewidth=1, color='k')
        self.getPlotAxes('Polos y Ceros 2').axvline(linewidth=1, color='k')

        poles_labels = dict()
        zeros_labels = dict()
        for i, pole in enumerate(p):
            self.getPlotAxes('Máximo Q').plot(pole.real, pole.imag, 'rx', markersize=10)
            self.getPlotAxes('Polos y Ceros 2').plot(pole.real, pole.imag, 'rx', markersize=10)
            Q = -abs(pole)/(2*pole.real) if pole.real < 0 else float('inf')
            xy = (pole.real, pole.imag)
            poles_labels[xy] = '{} \n Q = {:.3f} \n (Polo n°{}'.format(name, Q, i+1) if xy not in poles_labels else poles_labels[xy]+', '+ str(i+1)
        for i, zero in enumerate(z):
            self.getPlotAxes('Máximo Q').plot(zero.real, zero.imag, 'bo', markersize=10, fillstyle='none')
            self.getPlotAxes('Polos y Ceros 2').plot(zero.real, zero.imag, 'bo', markersize=10, fillstyle='none')
            xy = (zero.real, zero.imag)
            zeros_labels[xy] = '{} \n Cero n°'.format(name) + str(i + 1) if xy not in zeros_labels else zeros_labels[xy] + ', ' + str(i + 1)

        for polexy in poles_labels:
            self.getPlotAxes('Máximo Q').annotate(poles_labels[polexy]+')', polexy, textcoords="offset points", xytext=(0, 10), ha='center')
            self.getPlotAxes('Polos y Ceros 2').annotate(poles_labels[polexy]+')', polexy, textcoords="offset points", xytext=(0, 10), ha='center')
        for zeroxy in zeros_labels:
            self.getPlotAxes('Máximo Q').annotate(zeros_labels[zeroxy], zeroxy, textcoords="offset points", xytext=(0, 10), ha='center')
            self.getPlotAxes('Polos y Ceros 2').annotate(zeros_labels[zeroxy], zeroxy, textcoords="offset points", xytext=(0, 10), ha='center')

        self.getPlotAxes('Polos y Ceros 2').axis('equal')
        self.getPlotAxes('Máximo Q').axis('equal')

        return

    def newStage(self):
        index = self.combo_filtro.currentIndex()
        new_stage = self.getStageParameters(index)
        if new_stage is not None:
            self.stage_list.addItem(new_stage.getLabel(self.filters[index].filter_design, self.filters[index].designconfig.name))
            self.filters[index].filter_stages[new_stage.getLabel(self.filters[index].filter_design, self.filters[index].designconfig.name)] = new_stage
            return True
        return False

    def getStageParameters(self, index):
        pole1 = self.combo_polo1.currentText()
        pole2 = self.combo_polo2.currentText()
        pole1 = int(pole1[7:]) - 1 if pole1.startswith('Polo n°') else -1
        pole2 = int(pole2[7:]) - 1 if pole2.startswith('Polo n°') else -1

        zero1 = self.combo_cero1.currentText()
        zero2 = self.combo_cero2.currentText()
        zero1 = int(zero1[7:]) - 1 if zero1.startswith('Cero n°') else -1
        zero2 = int(zero2[7:]) - 1 if zero2.startswith('Cero n°') else -1

        gain = self.spin_gain.value()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Advertencia")
        if pole1 == pole2 and pole1 >= 0:
            msg.setText("Los polos deben ser distintos.")
            msg.exec_()
        elif zero1 == zero2 and zero1 >= 0:
            msg.setText("Los ceros deben ser distintos.")
            msg.exec_()
        elif pole1 == pole2 and zero1 == zero2 and pole1 < 0 and zero1 < 0:
            msg.setText("Seleccionar al menos un polo o un cero.")
            msg.exec_()
        elif pole1 >= 0 and pole2 >= 0 and not np.isclose(self.filters[index].filter_design.poles[pole1].real, self.filters[index].filter_design.poles[pole2].real):
            print(self.filters[index].filter_design.poles[pole1].real, self.filters[index].filter_design.poles[pole2].real)
            msg.setText("Los polos deben ser complejos conjugados.")
            msg.exec_()
        elif zero1 >= 0 and zero2 >= 0 and not np.isclose(self.filters[index].filter_design.zeros[zero1].imag, -self.filters[index].filter_design.zeros[zero2].imag):
            msg.setText("Los ceros deben ser complejos conjugados.")
            msg.exec_()
        elif (zero1 >= 0 and self.filters[index].filter_design.zeros[zero1].imag != 0 and zero2 < 0) or ( zero2 >= 0 and self.filters[index].filter_design.zeros[zero2].imag != 0 and zero1 < 0):
            msg.setText("Los ceros deben ser complejos conjugados.")
            msg.exec_()
        elif ((zero1 >= 0 or zero2 >= 0) and (pole1 < 0 and pole2 < 0)) or ((zero1 >= 0 and zero2 >= 0) and (pole1 < 0 or pole2 < 0)):
            msg.setText("Las etapas deben contener un número mayor o igual de polos que de ceros.")
            msg.exec_()
        else:
            pole = None
            if pole1 >= 0:
                self.combo_polo1.model().item(pole1 + 1).setEnabled(False)
                self.combo_polo2.model().item(pole1 + 1).setEnabled(False)
                pole = self.filters[index].filter_design.poles[pole1]
            if pole2 >= 0:
                self.combo_polo1.model().item(pole2 + 1).setEnabled(False)
                self.combo_polo2.model().item(pole2 + 1).setEnabled(False)
                pole = self.filters[index].filter_design.poles[pole2]
            if zero1 >= 0:
                self.combo_cero1.model().item(zero1 + 1).setEnabled(False)
                self.combo_cero2.model().item(zero1 + 1).setEnabled(False)
            if zero2 >= 0:
                self.combo_cero1.model().item(zero2 + 1).setEnabled(False)
                self.combo_cero2.model().item(zero2 + 1).setEnabled(False)
            self.combo_polo1.setCurrentIndex(0)
            self.combo_polo2.setCurrentIndex(0)
            self.combo_cero1.setCurrentIndex(0)
            self.combo_cero2.setCurrentIndex(0)

            self.filters[index].gain_remaining -= gain
            self.label_gain_total.setText('Restante: {:.3f} dB'.format(self.filters[index].gain_remaining))

            Q = -abs(pole) / (2 * pole.real) if pole.real < 0 else float('inf')
            return FilterStage(pole1, pole2, zero1, zero2, gain, Q)

        return None

    def editStage(self):
        index = self.combo_filtro.currentIndex()
        if not self.filters[index].editingStage:
            selection = self.stage_list.selectedItems()
            if len(selection) > 0:
                self.btn_edit_stage.setText('Hecho')
                self.filters[index].editingStage = True
                self.filters[index].editingStageIndex = self.stage_list.row(selection[0])
                self.btn_new_stage.setEnabled(False)
                self.btn_plot_stage.setEnabled(False)
                self.btn_delete_stage.setEnabled(False)
                self.stage_list.setEnabled(False)
                index = self.filters[index].editingStageIndex
                current_stage = self.filters[index].filter_stages[self.stage_list.item(index).text()]
                pole1 = current_stage.pole1
                pole2 = current_stage.pole2
                zero1 = current_stage.zero1
                zero2 = current_stage.zero2
                gain = current_stage.gain
                self.spin_gain.setValue(gain)
                self.filters[index].gain_remaining += gain
                if pole1 >= 0:
                    self.combo_polo1.model().item(pole1 + 1).setEnabled(True)
                    self.combo_polo2.model().item(pole1 + 1).setEnabled(True)
                    self.combo_polo1.setCurrentIndex(pole1 + 1)
                if pole2 >= 0:
                    self.combo_polo1.model().item(pole2 + 1).setEnabled(True)
                    self.combo_polo2.model().item(pole2 + 1).setEnabled(True)
                    self.combo_polo2.setCurrentIndex(pole2 + 1)
                if zero1 >= 0:
                    self.combo_cero1.model().item(zero1 + 1).setEnabled(True)
                    self.combo_cero2.model().item(zero1 + 1).setEnabled(True)
                    self.combo_cero1.setCurrentIndex(zero1 + 1)
                if zero2 >= 0:
                    self.combo_cero1.model().item(zero2 + 1).setEnabled(True)
                    self.combo_cero2.model().item(zero2 + 1).setEnabled(True)
                    self.combo_cero2.setCurrentIndex(zero2 + 1)
                return True
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Advertencia")
                msg.setText("Seleccionar una etapa para editar.")
                msg.exec_()
                return False
        else:
            new_stage = self.getStageParameters(index)
            if new_stage is not None:
                self.btn_edit_stage.setText('Editar')
                self.filters[index].editingStage = False
                self.btn_new_stage.setEnabled(True)
                self.btn_plot_stage.setEnabled(True)
                self.btn_delete_stage.setEnabled(True)
                self.stage_list.setEnabled(True)

                index = self.filters[index].editingStageIndex
                del self.filters[index].filter_stages[self.stage_list.item(index).text()]
                self.stage_list.item(index).setText(new_stage.getLabel(self.filters[index].filter_design, self.filters[index].designconfig.name))
                self.filters[index].filter_stages[new_stage.getLabel(self.filters[index].filter_design, self.filters[index].designconfig.name)] = new_stage
                return True
            else:
                return False

    def plotStage(self):
        selection = self.stage_list.selectedItems()
        if len(selection) > 0:
            indice = self.combo_filtro.currentIndex() 
            index = self.stage_list.row(selection[0])
            stage = self.filters[indice].filter_stages[self.stage_list.item(index).text()]
            poles = []
            zeros = []
            if stage.pole1 >= 0:
                poles.append(self.filters[indice].filter_design.poles[stage.pole1])
            if stage.pole2 >= 0:
                poles.append(self.filters[indice].filter_design.poles[stage.pole2])

            if stage.zero1 >= 0:
                zeros.append(self.filters[indice].filter_design.zeros[stage.zero1])
            if stage.zero2 >= 0:
                zeros.append(self.filters[indice].filter_design.zeros[stage.zero2])

            zpg = signal.ZerosPolesGain(zeros,poles,1)
            H = signal.TransferFunction(zpg)
            H.num = H.num * 10**(stage.gain/20)
            Gain = signal.bode(H)
            
            freq = Gain[0] / (2* pi)

            self.getPlotAxes('Respuesta Etapa').clear()
            self.getPlotAxes('Respuesta Etapa').grid()
            self.getPlotAxes('Respuesta Etapa').semilogx(freq, Gain[1], label = self.filters[indice].designconfig.name)
            self.axes2[2].set_xlabel('Frecuencia [Hz]')
            self.axes2[2].set_ylabel('Amplitud [dB]')
            self.axes2[2].legend()
            self.figure2[2].tight_layout()
            self.canvas2[2].draw()
            return True
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia")
            msg.setText("Seleccionar una etapa para graficar.")
            msg.exec_()
            return False

    def deleteStage(self):
        indice = self.combo_filtro.currentIndex()
        selection = self.stage_list.selectedItems()
        if len(selection) > 0:
            index = self.stage_list.row(selection[0])
            old_stage = self.filters[indice].filter_stages[self.stage_list.takeItem(index).text()]
            pole1 = old_stage.pole1
            pole2 = old_stage.pole2
            zero1 = old_stage.zero1
            zero2 = old_stage.zero2
            gain = old_stage.gain
            self.filters[indice].gain_remaining += gain
            self.label_gain_total.setText('Restante: {:.3f} dB'.format(self.filters[indice].gain_remaining))
            if pole1 >= 0:
                self.combo_polo1.model().item(pole1 + 1).setEnabled(True)
                self.combo_polo2.model().item(pole1 + 1).setEnabled(True)
            if pole2 >= 0:
                self.combo_polo1.model().item(pole2 + 1).setEnabled(True)
                self.combo_polo2.model().item(pole2 + 1).setEnabled(True)
            if zero1 >= 0:
                self.combo_cero1.model().item(zero1 + 1).setEnabled(True)
                self.combo_cero2.model().item(zero1 + 1).setEnabled(True)
            if zero2 >= 0:
                self.combo_cero1.model().item(zero2 + 1).setEnabled(True)
                self.combo_cero2.model().item(zero2 + 1).setEnabled(True)
            del old_stage
            return True
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia")
            msg.setText("Seleccionar una etapa para borrar.")
            msg.exec_()
            return False

    def getPlotAxes(self, type):
        if type in self.plot_types:
            return self.axes[self.plot_types[type]]
        elif type in self.plot_types2:
            return self.axes2[self.plot_types2[type]]
    
    def updateStageView(self):
        pass  # TO-DO

    def addFilter(self):
        try:
            name = self.lineEdit.text()
            type = self.combo_tipo.currentText()
            aprox = self.combo_aprox.currentText()
            denorm = self.spin_denorm.value()
            minord = self.spin_minord.value()
            maxord = self.spin_maxord.value()
            qmax = self.spin_qmax.value()
            Ap = self.spin_Ap.value()
            ripple = self.spin_ripple.value()
            Aa = self.spin_Aa.value()
            wp = self.spin_wp.value() * 2 * pi
            wa = self.spin_wa.value() * 2 * pi
            wp2 = self.spin_wp_2.value() * 2 * pi
            wa2 = self.spin_wa_2.value() * 2 * pi
            tau = self.GD_tau.value()
            wrg = self.GD_wrg.value() * 2 * pi
            gamma = self.GD_gamma.value()

            # Mensaje advertencia: Parametros invalidos
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Advertencia")
            warning_msg = ''
            w_band = type == 'Pasa Banda' or type == 'Rechaza Banda'
            g_delay = type == 'Retardo de Grupo'
            if not g_delay:
                if (wp == 0 or wa == 0) or \
                    (w_band and (wp2 == 0 or wa2 == 0 or wp2 >= wp or wa2 >= wa)) or \
                    (type == 'Pasa Banda' and (wp >= wa or wp2 <= wa2)) or \
                    (type == 'Rechaza Banda' and (wp <= wa or wp2 >= wa2)) or \
                    (type == 'Pasa Bajos' and wa <= wp) or \
                    (type == 'Pasa Altos' and wp <= wa):
                        warning_msg += "Los parametros para fp y fa son inválidos.\n"
                if ripple <= 0:
                    warning_msg += "El valor máximo de ripple debe ser mayor a 0.\n"
                if Aa <= Ap:
                    warning_msg += "El valor de Aa debe ser mayor al valor de Ap.\n"
                if minord > maxord:
                    warning_msg += "El orden mínimo debe ser menor al orden máximo.\n"
            if len(warning_msg) > 0:
                msg.setText(warning_msg)
                msg.exec_()
            else:
                for x, ax in enumerate(self.axes):
                    ax.clear()
                    ax.grid()
                for x, ax in enumerate(self.axes2):
                    ax.clear()
                    ax.grid()

                filter_types = ['Pasa Bajos', 'Pasa Altos', 'Pasa Banda', 'Rechaza Banda', 'Retardo de Grupo']
            
                self.filters.append(Filter(designconfig = DesignConfig(name, filter_types.index(type), aprox, denorm, minord, maxord, qmax, Ap, ripple, Aa, wp, wa, wp2, wa2, tau, wrg, gamma), filter_design = FilterDesign()))
                self.updateFilterList()
                self.plotAll()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("No se pudo agregar el filtro.")
            msg.exec_()
            return False

    def updateFilterList(self):
        try:
            self.filters_list.clear()
            self.combo_filtro.clear()

            for f in self.filters:
                item = QtWidgets.QListWidgetItem(f.designconfig.name, self.filters_list)
                item.setCheckState(QtCore.Qt.Checked if f.visible else QtCore.Qt.Unchecked)
                #item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
                self.combo_filtro.addItem(f.designconfig.name)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("No se pudo actualizar la lista de filtros.")
            msg.exec_()
            return False

    def removeFilter(self):
        try:
            if self.filters:
                self.filters.pop(self.filters_list.currentRow())
                self.updateFilterList()
            self.plotAll()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("No se pudo eliminar el filtro.")
            msg.exec_()
            return False

    def onFilterItemChanged(self, item):
        try:
            if (len(self.filters)):
                index = self.filters_list.row(item)
                self.filters[index].visible = item.checkState() == QtCore.Qt.Checked
                self.filters[index].designconfig.name = item.text()
                self.combo_filtro.setItemText(index, self.filters[index].designconfig.name)

            self.plotAll()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("No se pudo actualizar los filtros.")
            msg.exec_()
            return False

    def updateStageMenu(self):
        self.stage_list.clear()
        self.combo_polo1.clear()
        self.combo_polo2.clear()
        self.combo_cero1.clear()
        self.combo_cero2.clear()
        self.combo_polo1.addItem('-')
        self.combo_polo2.addItem('-')
        self.combo_cero1.addItem('-')
        self.combo_cero2.addItem('-')

        if self.filters:
            p = self.filters[self.combo_filtro.currentIndex()].filter_design.poles.copy()
            z = self.filters[self.combo_filtro.currentIndex()].filter_design.zeros.copy()
            self.plotPolesAndZeros(z,p, self.filters[self.combo_filtro.currentIndex()].designconfig.name)

    def writeOrden(self):
        selected = self.filters_list.selectedItems()
        index = self.filters_list.row(selected[0])
        self.label_writeorden.setText(str(self.filters[index].orden))

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)