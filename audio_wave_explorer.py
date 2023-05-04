import numpy as np
from scipy.signal import *
from scipy.fftpack import fft
import sounddevice as sd
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys
import queue


class audio_wave_analyzer(QtWidgets.QWidget):
    def __init__(self):

        self.RATE = 44100   # Sample Rate
        self.CHUNK = 4410  # Block Size
        self.start_idx = 0  # Start index of the signal
        self.freq = 440     # Initial frequency
        self.types = ["Sine", "Sawtooth", "Triangular", "Square"]
        self.type = self.types[0]   # Initial waveform
        self.trigger = 0  # Initial trigger
        self.amplitude = 1      # Initial Amplitude
        self.amplification = 1      # Initial Amplitude

        sd.default.dtype = np.float32
        sd.default.samplerate = self.RATE
        self.ostream = sd.OutputStream(callback=self.Output_Callback)
        try:
            self.istream = sd.InputStream(
                blocksize=self.CHUNK, callback=self.Input_Callback)
            self.istream.start()
            self.q = queue.Queue(maxsize=1)
        except sd.PortAudioError as e:
            print(f"Error opening audio input stream: {e}")
            self.istream = None
            self.q = None

        super(audio_wave_analyzer, self).__init__()
        self.init_ui()
        self.qt_connections()
        self.plotcurve = pg.PlotCurveItem(pen="b")
        self.plotspectrum = pg.PlotCurveItem(pen="y")
        self.plotwidget.addItem(self.plotcurve)
        self.plotwidget2.addItem(self.plotspectrum)
        self.plotwidget.setLabel('bottom', 'Time (s)')
        self.plotwidget2.setLabel('bottom', 'Frequency (Hz)')
        self.plotwidget.setYRange(-1, 1)
        self.updateplot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(0)

    def init_ui(self):
        self.setWindowTitle('Audio Wave Analyzer')
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        self.plotwidget = pg.PlotWidget(title="Waveform")
        self.plotwidget2 = pg.PlotWidget(title="Spectrum")
        vbox.addWidget(self.plotwidget)
        vbox.addWidget(self.plotwidget2)

        self.playbutton = QtWidgets.QPushButton("Play")
        self.stopbutton = QtWidgets.QPushButton("Stop")
        self.playbutton.move(800, 600)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(self.playbutton)
        hbox.addWidget(self.stopbutton)

        waveform = QtWidgets.QLabel("Waveform:")
        ofreq = QtWidgets.QLabel("Output Freq:")
        amplitude = QtWidgets.QLabel("Amplitude:")
        trigger = QtWidgets.QLabel("Trigger:")
        amplification = QtWidgets.QLabel("Amplification:")
        chunk = QtWidgets.QLabel("Sweep time:")
        ifreq = QtWidgets.QLabel("Estimated Freq:")
        maxfreq = QtWidgets.QLabel("Max Freq:")
        self.ofreqedit = QtWidgets.QDoubleSpinBox()s
        self.triggeredit = QtWidgets.QDoubleSpinBox()
        self.amplitudeedit = QtWidgets.QDoubleSpinBox()
        self.amplificationedit = QtWidgets.QDoubleSpinBox()
        self.timeedit = QtWidgets.QDoubleSpinBox()
        self.freqmaxedit = QtWidgets.QSpinBox()
        self.readifreq = QtWidgets.QLineEdit()

        self.ofreqedit.setRange(0, 10000)
        self.ofreqedit.setSingleStep(0.1)
        self.ofreqedit.setValue(self.freq)
        self.ofreqedit.valueChanged.connect(self.ofreqchange)
        self.triggeredit.setRange(-1, 1)
        self.triggeredit.setSingleStep(0.01)
        self.triggeredit.setValue(self.trigger)
        self.triggeredit.valueChanged.connect(self.triggerchange)
        self.amplitudeedit.setRange(0, 1)
        self.amplitudeedit.setSingleStep(0.001)
        self.amplitudeedit.setDecimals(3)
        self.amplitudeedit.setValue(self.amplitude)
        self.amplitudeedit.valueChanged.connect(self.amplitudechange)
        self.amplificationedit.setRange(0, 10000)
        self.amplificationedit.setSingleStep(0.01)
        self.amplificationedit.setValue(self.amplification)
        self.amplificationedit.valueChanged.connect(self.amplificationchange)
        self.timeedit.setRange(0.01, 10)
        self.timeedit.setDecimals(5)
        self.timeedit.setSingleStep(0.00002)
        self.timeedit.setValue(self.CHUNK / self.RATE)
        self.timeedit.valueChanged.connect(self.timechange)
        self.freqmaxedit.setRange(100, self.RATE)
        self.freqmaxedit.setValue(self.RATE)
        self.freqmaxedit.valueChanged.connect(self.freqmaxchange)

        self.wavetype = QtWidgets.QComboBox()
        self.wavetype.addItems(self.types)
        self.wavetype.currentIndexChanged.connect(self.wavechange)

        salida = QtWidgets.QLabel("Output params:")
        salida.setFixedSize(100, 20)
        salida.setFont(QtGui.QFont("Arial", 9))
        entrada = QtWidgets.QLabel("Input params:")
        entrada.setFixedSize(100, 20)
        entrada.setFont(QtGui.QFont("Arial", 9))

        hbox2 = QtWidgets.QHBoxLayout()
        hbox3 = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox1 = QtWidgets.QVBoxLayout()
        vbox2 = QtWidgets.QVBoxLayout()
        vbox3 = QtWidgets.QVBoxLayout()
        vbox4 = QtWidgets.QVBoxLayout()
        vbox5 = QtWidgets.QVBoxLayout()
        vbox6 = QtWidgets.QVBoxLayout()
        vbox7 = QtWidgets.QVBoxLayout()
        vbox8 = QtWidgets.QVBoxLayout()
        hbox2.addWidget(salida)
        hbox3.addWidget(entrada)
        hbox2.addLayout(vbox1)
        hbox2.addLayout(vbox2)
        hbox2.addLayout(vbox3)
        hbox3.addLayout(vbox4)
        hbox3.addLayout(vbox5)
        hbox3.addLayout(vbox6)
        hbox3.addLayout(vbox7)
        hbox3.addLayout(vbox8)
        vbox1.addWidget(waveform)
        waveform.setAlignment(QtCore.Qt.AlignCenter)
        vbox2.addWidget(amplitude)
        amplitude.setAlignment(QtCore.Qt.AlignCenter)
        vbox3.addWidget(ofreq)
        ofreq.setAlignment(QtCore.Qt.AlignCenter)
        vbox4.addWidget(amplification)
        amplification.setAlignment(QtCore.Qt.AlignCenter)
        vbox5.addWidget(chunk)
        chunk.setAlignment(QtCore.Qt.AlignCenter)
        vbox6.addWidget(trigger)
        trigger.setAlignment(QtCore.Qt.AlignCenter)
        vbox7.addWidget(ifreq)
        ifreq.setAlignment(QtCore.Qt.AlignCenter)
        vbox8.addWidget(maxfreq)
        ifreq.setAlignment(QtCore.Qt.AlignCenter)
        vbox1.addWidget(self.wavetype)
        vbox2.addWidget(self.amplitudeedit)
        vbox3.addWidget(self.ofreqedit)
        vbox4.addWidget(self.amplificationedit)
        vbox5.addWidget(self.timeedit)
        vbox6.addWidget(self.triggeredit)
        vbox7.addWidget(self.readifreq)
        vbox8.addWidget(self.freqmaxedit)

        self.setGeometry(50, 50, 1000, 600)
        self.show()

    def qt_connections(self):
        self.playbutton.clicked.connect(self.on_playbutton_clicked)
        self.stopbutton.clicked.connect(self.on_stopbutton_clicked)

    def updateplot(self):
        if self.q is None:
            return
        try:
            data = self.q.get_nowait()[:, 0]
        except queue.Empty:
            return
        spdata = np.abs(fft(data))
        spdata = spdata / np.max(spdata)
        data = data * self.amplification
        for x in range(len(data) - 1):
            index = x
            if (data[x] <= self.trigger) and (data[x + 1] > self.trigger):
                break
        self.x = np.linspace(
            0, len(data[index:]) / self.RATE, len(data[index:]))
        self.f = np.linspace(0, self.RATE / 2, int(len(data) / 2))
        self.plotcurve.setData(self.x, data[index:])
        self.plotspectrum.setData(
            self.f, spdata[:int(len(data) / 2)])
        self.plotwidget.setXRange(0, len(data) / self.RATE)
        spdata2 = spdata[::2]
        spdata3 = spdata[::3]
        size = spdata3.size
        sp = spdata[:size] * spdata2[:size] * spdata3[:size] * spdata3
        self.readifreq.setText(str(self.RATE * np.argmax(sp) / self.CHUNK))

    def on_playbutton_clicked(self):
        self.ostream.start()

    def on_stopbutton_clicked(self):
        self.ostream.stop()

    def ofreqchange(self):
        self.freq = self.ofreqedit.value()

    def triggerchange(self):
        self.trigger = self.triggeredit.value()

    def amplitudechange(self):
        self.amplitude = self.amplitudeedit.value()

    def amplificationchange(self):
        self.amplification = self.amplificationedit.value()

    def timechange(self):
        if self.istream is None:
            return
        self.CHUNK = int(self.timeedit.value() * self.RATE)
        self.istream.stop()
        self.istream = sd.InputStream(
            blocksize=self.CHUNK, callback=self.Input_Callback)
        self.istream.start()

    def freqmaxchange(self):
        self.plotwidget2.setXRange(0, self.freqmaxedit.value())

    def wavechange(self):
        self.type = self.wavetype.currentText()

    def Output_Callback(self, outdata, frames, _, status):
        if status:
            print(status, file=sys.stderr)
        t = (self.start_idx + np.arange(frames)) / self.RATE
        t = t.reshape(-1, 1)
        if self.type == self.types[0]:
            outdata[:] = np.sin(2 * np.pi * self.freq * t)
        if self.type == self.types[1]:
            outdata[:] = sawtooth(2 * np.pi * self.freq * t, 1)
        if self.type == self.types[2]:
            outdata[:] = sawtooth(2 * np.pi * self.freq * t, 0.5)
        if self.type == self.types[3]:
            outdata[:] = square(2 * np.pi * self.freq * t)
        outdata[:] = outdata[:] * self.amplitude
        self.start_idx += frames

    def Input_Callback(self, indata, frames, _, status):
        if self.istream is None or self.q is None:
            return
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Audio Wave Analyzer')
    ex = audio_wave_analyzer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
