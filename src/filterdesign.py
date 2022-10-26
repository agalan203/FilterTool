from src.filterstage import *
from src.designconfiguration import *
from src.approximations import *

import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi

class FilterDesign:
    def __init__(self, dc = None, gain = 0, stages = None, poles = [], zeros = []):
        #Circuit design
        self.dc = dc
        self.gain = gain
        self.stages = stages
        self.poles = poles
        self.zeros = zeros

    def setPolesAndZeros(self, p, z):
        self.poles = p.copy()
        self.zeros = z.copy()

    def setDesignConfig(self, dc):
        self.dc = dc

    def setFilterStages(self, stages):
        self.stages = stages

    def save(self, filename):
        with open(filename, "w") as f:
            f.write('# TC 2022 - Grupo 1: Filter Tool\n')

            f.write('Design Configuration\n')
            if self.dc != None:
                f.write(str(self.dc))

            f.write('Gain\n')
            f.write('{}\n'.format(self.gain))

            f.write('Poles\n')
            if len(self.poles) > 0:
                for p in self.poles:
                    f.write(str(p))
                    f.write('\n')

            f.write('Zeros\n')
            if len(self.zeros) > 0:
                for z in self.zeros:
                    f.write(str(z))
                    f.write('\n')

            f.write('FilterStages\n')
            if self.stages != None:
                for stage in self.stages.values():
                    f.write(str(stage))

                    
    def open(self, filename):
        with open(filename, "r") as f:
            name = os.path.splitext(os.path.basename(filename))[0]
            lines = f.readlines()
            for i in range(len(lines)):
                lines[i] = lines[i].rstrip()
            i = 0
            while lines[i] != 'Design Configuration': i += 1
            type = int(lines[i + 1])
            aprox = str(lines[i + 2])
            denorm = int(lines[i + 3])
            minord = int(lines[i + 4])
            maxord = int(lines[i + 5])
            qmax = int(lines[i + 6])
            Ap = float(lines[i + 7])
            ripple = float(lines[i + 8])
            Aa = float(lines[i + 9])
            wp = float(lines[i + 10])
            wa = float(lines[i + 11])
            wp2 = float(lines[i + 12])
            wa2 = float(lines[i + 13])
            tau = float(lines[i + 14])
            wrg = float(lines[i + 15])
            gamma = int(lines[i + 16])
            i = i + 17

            self.dc = DesignConfig(name, type, aprox, denorm, minord, maxord, qmax, Ap, ripple, Aa, wp, wa, wp2, wa2, tau,
                                   wrg, gamma)

            while lines[i] != 'Gain': i += 1
            i += 1
            self.gain = float(lines[i])

            while lines[i] != 'Poles': i += 1
            i += 1
            self.poles = list()
            while lines[i] != 'Zeros':
                self.poles.append(complex(lines[i]))
                i += 1

            i += 1
            self.zeros = list()
            while lines[i] != 'FilterStages':
                self.zeros.append(complex(lines[i]))
                i += 1
                
            i += 1
            self.stages = dict()
            while i < len(lines) and len(lines[i]) > 0:
                pole1 = int(lines[i])
                pole2 = int(lines[i + 1])
                zero1 = int(lines[i + 2])
                zero2 = int(lines[i + 3])
                gain = float(lines[i + 4])
                Q = float(lines[i + 5])
                new_stage = FilterStage(pole1, pole2, zero1, zero2, gain, Q)
                self.stages[new_stage.getLabel(self, name)] = new_stage 
                i += 6
        return

    def export(self, filename):
        with PdfPages(filename) as pdf:
            firstPage = plt.figure(figsize=(8.27, 11.69))
            firstPage.clf()
            txt = 'TC 2022 - Grupo 1: Filter Tool'
            firstPage.text(0.5, 0.9, txt, transform=firstPage.transFigure, size=24, ha="center")
            txt = 'Configuraciones de diseño'
            firstPage.text(0.5, 0.6, txt, transform=firstPage.transFigure, size=18, va="top", ha="center")
            txt = self.dc.export_names()
            firstPage.text(0.275, 0.55, txt, transform=firstPage.transFigure, size=12, va="top", ha="left")
            txt = self.dc.export_values()
            firstPage.text(0.625, 0.55, txt, transform=firstPage.transFigure, size=12, va="top", ha="left")
            pdf.savefig()
            plt.close()

            type = self.dc.filter_types[self.dc.type]
            w_band = type == 'Pasa Banda' or type == 'Rechaza Banda'
            g_delay = type == 'Retardo de Grupo'
            attenuationPage = plt.figure(figsize=(11.69, 8.27))
            attenuationPage.clf()
            plt.grid()

            self.gain = self.dc.ripple - self.dc.Ap
            aprox = self.dc.aprox
            denorm = self.dc.denorm
            minord = self.dc.minord
            maxord = self.dc.maxord
            qmax = self.dc.qmax
            Ap = self.dc.Ap
            ripple = self.dc.ripple
            Aa = self.dc.Aa
            wp = self.dc.wp
            wa = self.dc.wa
            wp2 = self.dc.wp2
            wa2 = self.dc.wa2
            tau = self.dc.tau
            wrg = self.dc.wrg
            gamma = self.dc.gamma

            if type == 'Pasa Bajos':
                x = [wp / 10 / (2*pi), wp/ (2*pi), wp/ (2*pi)]
                y = [Ap, Ap, Aa + 10]
                if Ap <= 0:
                    yR = [Ap - ripple, Ap - ripple]
                else:
                    yR = [ripple, ripple]
                plt.semilogx(x[:-1], yR, '-', color='#1a6125', linewidth=2)
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
                x = [wa/ (2*pi), wa/ (2*pi), wa * 10/ (2*pi)]
                y = [Ap - 10, Aa, Aa]
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            elif type == 'Pasa Altos':
                x = [wa / 10/ (2*pi), wa/ (2*pi), wa/ (2*pi)]
                y = [Aa, Aa, Ap - 10]
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
                x = [wp/ (2*pi), wp/ (2*pi), wp * 10/ (2*pi)]
                y = [Aa + 10, Ap, Ap]
                if Ap <= 0:
                    yR = [Ap - ripple, Ap - ripple]
                else:
                    yR = [ripple, ripple]
                plt.semilogx(x[1:], yR, '-', color='#1a6125', linewidth=2)
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            elif type == 'Pasa Banda':
                x = [wa2 / 10/ (2*pi), wa2/ (2*pi), wa2/ (2*pi)]
                y = [Aa, Aa, Ap - 10]
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
                x = [wp2/ (2*pi), wp2/ (2*pi), wp/ (2*pi), wp/ (2*pi)]
                y = [Aa + 10, Ap, Ap, Aa + 10]
                if Ap <= 0:
                    yR = [Ap - ripple, Ap - ripple]
                else:
                    yR = [ripple, ripple]
                plt.semilogx(x[1:-1], yR, '-', color='#1a6125', linewidth=2)
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
                x = [wa/ (2*pi), wa/ (2*pi), wa * 10/ (2*pi)]
                y = [Ap - 10, Aa, Aa]
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            elif type == 'Rechaza Banda':
                x = [wp2 / 10/ (2*pi), wp2/ (2*pi), wp2/ (2*pi)]
                y = [Ap, Ap, Aa + 10]
                if Ap <= 0:
                    yR = [Ap - ripple, Ap - ripple]
                else:
                    yR = [ripple, ripple]
                plt.semilogx(x[:-1], yR, '-', color='#1a6125', linewidth=2)
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
                x = [wa2/ (2*pi), wa2/ (2*pi), wa/ (2*pi), wa/ (2*pi)]
                y = [Ap - 10, Aa, Aa, Ap - 10]
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
                x = [wp/ (2*pi), wp/ (2*pi), wp * 10/ (2*pi)]
                y = [Aa + 10, Ap, Ap]
                if Ap <= 0:
                    yR = [Ap - ripple, Ap - ripple]
                else:
                    yR = [ripple, ripple]
                plt.semilogx(x[1:], yR, '-', color='#1a6125', linewidth=2)
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.max(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)

            # Calcular aproximación
            if aprox == 'Butterworth':
                z, p, k, n = Butterworth(self.dc)
            elif aprox == 'Chebyshev I':
                z, p, k, n = ChebyshevI(self.dc)
            elif aprox == 'Chebyshev II':
                z, p, k, n = ChebyshevI(self.dc)
            elif aprox == 'Bessel':
                z, p, k, n = Bessel(self.dc)
            elif aprox == 'Cauer':
                z, p, k, n = Cauer(self.dc)
            elif aprox == 'Gauss':
                z, p, k, n = Gauss(self.dc)
            elif aprox == 'Legendre':
                z, p, k, n = Legendre(self.dc)

            if Ap <= 0:
                k *= 10 ** (self.gain / 20)
            filter_system = signal.ZerosPolesGain(z, p, k)
            # Atenuacion y Fase
            if type == 'Pasa Bajos' or type == 'Pasa Altos':
                lowerfreq = wp / 10
                higherfreq = wa * 10
            elif type == 'Pasa Banda' or type == 'Rechaza Banda':
                lowerfreq = min(wa, wp, wa2, wp2) / 10
                higherfreq = max(wa, wp, wa2, wp2) * 10
            elif aprox == 'Bessel' or aprox == 'Gauss':
                lowerfreq = wrg / 10
                higherfreq = wrg * 10

            x = np.logspace((np.log10(lowerfreq)), (np.log10(higherfreq)), num=1000)
            Gain = signal.bode(filter_system, x)
            Attenuation = signal.bode(signal.ZerosPolesGain(p, z, 1 / k), x)
            freq = Attenuation[0] / (2* pi)
            freq1 = Gain[0] / (2* pi)
            plt.semilogx(freq, Attenuation[1], 'k')
            plt.title('Atenuación')
            plt.xlabel('Frecuencia [Hz]')
            plt.ylabel('Atenuación [dB]')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            phasePage = plt.figure(figsize=(11.69, 8.27))
            phasePage.clf()
            plt.grid()
            plt.semilogx(freq1, Gain[2], 'k')
            plt.title('Fase')
            plt.xlabel('Frecuencia [Hz]')
            plt.ylabel('Fase [°]')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            responsePage = plt.figure(figsize=(11.69, 8.27))
            responsePage.clf()
            plt.grid()
            plt.semilogx(freq1, Gain[1], 'k')
            plt.title('Respuesta en frecuencia total')
            plt.xlabel('Frecuencia [Hz]')
            plt.ylabel('Amplitud [dB]')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            gdelayPage = plt.figure(figsize=(11.69, 8.27))
            gdelayPage.clf()
            plt.grid()
            w, h = signal.freqs_zpk(z, p, k, x)
            gd = -np.diff(np.unwrap(np.angle(h))) / np.diff(w)
            plt.semilogx(w[1:], gd, 'k')
            if aprox == 'Bessel' or aprox == 'Gauss':
                x = [wrg / 10, wrg, wrg]
                y = [tau - (tau * gamma / 100), tau - (tau * gamma / 100), 0]
                plt.semilogx(x, y, '-', color='#1a6125', linewidth=2)
                plt.fill_between(x, y, np.min(y), facecolor='#7fb587', alpha=0.5, edgecolor='#3d6343', linewidth=0)
            plt.title('Retardo de Grupo')
            plt.xlabel('Frecuencia [Hz]')
            plt.ylabel('Tiempo [s]')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            polesPage = plt.figure(figsize=(11.69, 8.27))
            polesPage.clf()
            plt.grid()
            plt.axhline(linewidth=1, color='k')
            plt.axvline(linewidth=1, color='k')
            poles_labels = dict()
            zeros_labels = dict()
            for i, pole in enumerate(p):
                plt.plot(pole.real, pole.imag, 'rx', markersize=10)
                xy = (pole.real, pole.imag)
                Q = -abs(pole)/(2*pole.real) if pole.real < 0 else float('inf')
                xy = (pole.real, pole.imag)
                poles_labels[xy] = 'Q = {:.3f}\n (Polo n°{}'.format(Q, i+1) if xy not in poles_labels else poles_labels[xy]+', '+ str(i+1)
            for i, zero in enumerate(z):
                plt.plot(zero.real, zero.imag, 'bo', markersize=10, fillstyle='none')
                xy = (zero.real, zero.imag)
                zeros_labels[xy] = 'Cero n°' + str(i + 1) if xy not in zeros_labels else zeros_labels[xy] + ', ' + str(i + 1)
            for polexy in poles_labels:
                plt.annotate(poles_labels[polexy]+')', polexy, textcoords="offset points", xytext=(0, 10), ha='center')
            for zeroxy in zeros_labels:
                plt.annotate(zeros_labels[zeroxy], zeroxy, textcoords="offset points", xytext=(0, 10), ha='center')
            plt.title('Polos y Ceros')
            plt.xlabel('σ')
            plt.ylabel('jω')
            plt.axis('equal')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            stepPage = plt.figure(figsize=(11.69, 8.27))
            stepPage.clf()
            plt.grid()
            t, y = signal.step(filter_system, N=1000)
            plt.plot(t, y, 'k')
            plt.title('Respuesta al Escalón')
            plt.xlabel('Tiempo [s]')
            plt.ylabel('Tensión [V]')
            plt.tight_layout()
            pdf.savefig()
            plt.close()