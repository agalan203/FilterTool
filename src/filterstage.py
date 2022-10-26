from scipy import signal

class FilterStage:
    def __init__(self, p1 = -1, p2 = -1, z1 = -1, z2 = -1, g = -1, Q = -1):
        self.pole1 = p1
        self.pole2 = p2
        self.zero1 = z1
        self.zero2 = z2
        self.gain = g
        self.Q = Q

    def setPoles(self, p1, p2):
        self.pole1 = p1
        self.pole2 = p2

    def getPoles(self):
        return self.pole1, self.pole2

    def getLabel(self, filterdesign, name):
        pole_text = ''
        zero_text = ''
        if self.pole1 < 0:
            pole_text = ' Polo n°{}\n'.format(self.pole2+1)
        elif self.pole2 < 0:
            pole_text = ' Polo n°{}\n'.format(self.pole1+1)
        else:
            pole_text = ' Polo n°{}, Polo n°{}\n'.format(self.pole1+1, self.pole2+1)
        if self.zero1 < 0:
            if self.zero2 >= 0:
                zero_text = ' Cero n°{}\n'.format(self.zero2+1)
        elif self.zero2 < 0:
            zero_text = ' Cero n°{}\n'.format(self.zero1+1)
        else:
            zero_text = ' Cero n°{}, Cero n°{}\n'.format(self.zero1+1, self.zero2+1)
        
        poles = []
        zeros = []
        if self.pole1 >= 0:
            poles.append(filterdesign.poles[self.pole1])
        if self.pole2 >= 0:
            poles.append(filterdesign.poles[self.pole2])

        if self.zero1 >= 0:
            zeros.append(filterdesign.zeros[self.zero1])
        if self.zero2 >= 0:
            zeros.append(filterdesign.zeros[self.zero2])
        
        zpg = signal.ZerosPolesGain(zeros,poles,1)
        H = signal.TransferFunction(zpg)
        if not zeros or H.num[len(H.num)-1]:
                a,b = signal.normalize(H.num, H.den)
                H = signal.TransferFunction(a/a[-1],b/b[-1])
        elif not H.num[len(H.num)-1] and len(H.num) == 2:
                H.num = H.num * H.den[1]

        H.num = H.num * 10**(self.gain/20)

        rightnum = ",".join((map("{:.3f}".format, H.num)))
        rightdenom = ",".join(map("{:.3f}".format, H.den))
        num_text = 'Numerador = [{}]\n'.format(rightnum)
        denom_text = ' Denominador = [{}]\n'.format(rightdenom)

        return '{}\n{}{} Ganancia = {:.3f} dB\n Q = {:.3f}\n {}{}'.format(name, pole_text, zero_text, self.gain, self.Q, num_text, denom_text)

    def __str__(self):
        return '{}\n{}\n{}\n{}\n{}\n{}\n'.format(self.pole1, self.pole2, self.zero1, self.zero2, self.gain, self.Q)