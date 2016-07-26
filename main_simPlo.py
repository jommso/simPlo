import sys
import math
import time
import copy
import sys
from ui_simPlo import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QMenu, QAction, QInputDialog
from PyQt5.QtGui import QIcon, QGuiApplication, QStandardItem
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# plt.style.use("ggplot")
# simPlo unstable

class simPlo(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(simPlo, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("simPlo")
        self.setWindowIcon(QIcon('icons/simplo__symbol_green_red.png'))
        self.statusbar.showMessage("simPlo 1.0 - Jorge Soares")

        # matplotlib

        self.schrift = 12
        self.comment = ""

        self.ax = []
        self.figure = plt.figure(facecolor='white', edgecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.verticalLayout_mpl1.addWidget(self.canvas)
        self.ax.append(self.figure.add_subplot(111, frameon=True))  # axisbg='w',
        plt.gcf().subplots_adjust(bottom=0.18)

        self.figure2 = plt.figure(facecolor='white', edgecolor='black')
        self.canvas2 = FigureCanvas(self.figure2)
        self.verticalLayout_mpl1.addWidget(self.canvas2)
        self.ax.append(self.figure2.add_subplot(111, axisbg='w', frameon=True))
        plt.gcf().subplots_adjust(bottom=0.18)

        # Die Datenbank
        self.datenbank = []

        # treewidget
        self.elemente = []
        self.spalten = []
        self.treeWidget.headerItem().setText(0, "Data")
        self.treeWidget.headerItem().setText(1, "Axis")
        self.treeWidget.headerItem().setText(2, "ID")
        self.treeWidget.headerItem().setText(3, "Conn.")
        self.treeWidget.headerItem().setToolTip(3, "Connection")
        self.treeWidget.headerItem().setText(4, "Units")
        self.treeWidget.headerItem().setText(5, "Window")
        self.treeWidget.header().moveSection(4, 1)

        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeWidget.itemSelectionChanged.connect(self.fill_tab)

        # Tab-Gruppen
        self.lineEdit_legend.returnPressed.connect(self.change_legend_in_db)
        self.lineEdit_legend.setDisabled(False)
        self.lineEdit_id.setDisabled(True)
        self.lineEdit_connection.setDisabled(True)
        self.lineEdit_units.returnPressed.connect(self.change_unit_in_db)
        self.lineEdit_units.setDisabled(False)

        # das Kontextmenu
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.xwert = QAction(QIcon("icons/x-axis.png"), "X-Axis", self)
        self.xwert.setShortcut("Alt+x")
        self.xwert.triggered.connect(self.x_achse)
        self.treeWidget.addAction(self.xwert)

        self.ywert = QAction(QIcon("icons/y-axis.png"), "Y-Axis", self)
        self.ywert.setShortcut("Alt+y")
        self.ywert.triggered.connect(self.y_achse)
        self.treeWidget.addAction(self.ywert)

        self.verbinden = QAction(QIcon("icons/connect.png"), "Connect", self)
        self.verbinden.setShortcut("Alt+c")
        self.verbinden.triggered.connect(self.connect_the_data)
        self.treeWidget.addAction(self.verbinden)

        self.trennen = QAction(QIcon("icons/disconnect.png"), "Disconnect", self)
        self.trennen.setShortcut("Alt+d")
        self.trennen.triggered.connect(self.disconnect_the_data)
        self.treeWidget.addAction(self.trennen)

        self.plot_window_1 = QAction(QIcon("icons/add_1.png"), "Add to Chart one", self)
        self.plot_window_1.setShortcut("Alt+1")
        self.plot_window_1.triggered.connect(self.pl_wi_1)
        self.treeWidget.addAction(self.plot_window_1)

        self.plot_window_2 = QAction(QIcon("icons/add_2.png"), "Add to Chart two", self)
        self.plot_window_2.setShortcut("Alt+2")
        self.plot_window_2.triggered.connect(self.pl_wi_2)
        self.treeWidget.addAction(self.plot_window_2)

        self.plot_window_none = QAction(QIcon("icons/add_0.png"), "None Chart", self)
        self.plot_window_none.setShortcut("Alt+3")
        self.plot_window_none.triggered.connect(self.pl_wi_n)
        self.treeWidget.addAction(self.plot_window_none)

        self.plotten_starten = QAction(QIcon("icons/plot.png"), "Plot", self)
        self.plotten_starten.setShortcut("Alt+w")
        self.plotten_starten.triggered.connect(self.start_plot)
        # self.treeWidget.addAction(self.plotten_starten)

        self.delete_item = QAction("Delete", self)
        self.delete_item.setShortcut("Ctrl+x")
        self.delete_item.triggered.connect(self.delete_selected_data)
        self.treeWidget.addAction(self.delete_item)



        # Menubar
        menuleiste = self.menuBar()
        file = menuleiste.addMenu("&File")

        open_simplo = QAction("&Open simPlo - File", self)
        open_simplo.setShortcut("Ctrl+O")
        open_simplo.triggered.connect(self.load_simplo_format)
        open_simplo.setStatusTip("Open simPlo Database")

        save_simplo = QAction("&Save simPlo - File", self)
        save_simplo.setShortcut("Ctrl+E")
        save_simplo.triggered.connect(self.save_simplo_format)
        save_simplo.setStatusTip("Save simPlo Database")

        import_data = QAction(QIcon("icons/import.png"), "&Import CSV", self)
        import_data.setShortcut("Ctrl+I")
        import_data.triggered.connect(self.import_csv)

        export_data = QAction(QIcon("icons/export.png"), "&Export CSV", self)
        # export_data.setShortcut("Ctrl+I")
        export_data.triggered.connect(self.export_csv)

        exitMe = QAction("&Exit", self)
        # exitMe.setShortcut("Ctrl+E")
        exitMe.triggered.connect(self.sigint_handler)

        copy_d = QAction(QIcon("icons/duplicate.png"), "&Duplicate", self)
        save_simplo.setShortcut("Ctrl+D")
        copy_d.triggered.connect(self.duplicate_proc)
        # copy_d.setStatusTip("Save simPlo Database")

        integral_num = QAction(QIcon("icons/diff.png"), "Numerical Differentiation", self)
        integral_num.triggered.connect(self.diff_proc)

        math_op = QAction(QIcon("icons/math_op.png"), "Math Operations", self)
        math_op.triggered.connect(self.math_operations)


        self.save1 = QAction(QIcon("icons/save1.png"), "Save Plot 1", self)
        #self.delete_item.setShortcut("Ctrl+x")
        self.save1.triggered.connect(self.save_plot_1)

        self.save2 = QAction(QIcon("icons/save2.png"), "Save Plot 2", self)
        # self.delete_item.setShortcut("Ctrl+x")
        self.save2.triggered.connect(self.save_plot_2)

        file.addAction(open_simplo)
        file.addAction(save_simplo)
        file.addAction(import_data)
        file.addAction(self.delete_item)
        file.addAction(exitMe)

        file = menuleiste.addMenu("&Edit")
        file.addAction(self.xwert)
        file.addAction(self.ywert)
        file.addAction(self.verbinden)
        file.addAction(self.trennen)
        file.addAction(self.plot_window_1)
        file.addAction(self.plot_window_2)
        file.addAction(self.plot_window_none)
        file.addAction(self.plotten_starten)

        file = menuleiste.addMenu("&Processing")
        file.addAction(copy_d)
        file.addAction(integral_num)
        file.addAction(math_op)
        file.addAction(self.save1)
        file.addAction(self.save2)

        werkzeugleiste = self.addToolBar("Werkzeugleiste")
        werkzeugleiste.setIconSize(QtCore.QSize(40, 40))
        werkzeugleiste.addAction(export_data)
        werkzeugleiste.addAction(import_data)
        werkzeugleiste.addAction(self.xwert)
        werkzeugleiste.addAction(self.ywert)
        werkzeugleiste.addAction(self.verbinden)
        werkzeugleiste.addAction(self.trennen)
        werkzeugleiste.addAction(self.plot_window_1)
        werkzeugleiste.addAction(self.plot_window_2)
        werkzeugleiste.addAction(self.plot_window_none)
        werkzeugleiste.addSeparator()
        werkzeugleiste.addAction(self.plotten_starten)
        werkzeugleiste.addAction(self.save1)
        werkzeugleiste.addAction(self.save2)
        werkzeugleiste.addSeparator()
        werkzeugleiste.addAction(copy_d)
        werkzeugleiste.addAction(integral_num)
        werkzeugleiste.addAction(math_op)

        # TabWidget
        self.tabWidget.setCurrentIndex(0)

        # plot-events

        self.comboBox_linestyle_w1.currentTextChanged.connect(self.change_lineproperties_in_db)
        self.doubleSpinBox_linewidth_w1.valueChanged.connect(self.change_lineproperties_in_db)
        self.comboBox_marker_w1.currentTextChanged.connect(self.change_lineproperties_in_db)
        self.doubleSpinBox_markersize_w1.valueChanged.connect(self.change_lineproperties_in_db)
        self.plainTextEdit_comments.textChanged.connect(self.change_comments)
        self.pushButton_save_comment.pressed.connect(self.save_comment_to_db)

        self.lineEdit_xlabel_w1.setText("X-Axis")
        self.lineEdit_ylabel_w1.setText("Y-Axis")
        self.lineEdit_xlabel_w2.setText("X-Axis")
        self.lineEdit_ylabel_w2.setText("Y-Axis")
        self.lineEdit_title_w1.setText("Chart 1")
        self.lineEdit_title_w2.setText("Chart 2")


    # load an save
    def save_simplo_format(self):
        if len(self.datenbank) > 0:  # sind Daten vorhanden?
            f1 = QFileDialog.getSaveFileName(self, "Save SimPlo File", "",
                                             "SimPlo File (*.spl);;All Files (*)")
            if f1[0] == "": return

            fobj = open(f1[0], "w")
            for eintrag in self.datenbank:
                fobj.write("<start>\n")
                fobj.write(str(eintrag[0]) + "\n")  # 0: Dateiname
                fobj.write(str(eintrag[1]) + "\n")  # 1: Legende (Kopfzeile)
                fobj.write("<data>\n")
                for d in eintrag[2]:  # 2: Daten
                    fobj.write(str(d) + "\n")
                fobj.write("</data>\n")
                fobj.write(str(eintrag[3]) + "\n")  # 3: Achsentyp
                fobj.write(str(eintrag[4]) + "\n")  # 4: ID
                fobj.write(str(eintrag[5]) + "\n")  # 5: Connection
                fobj.write(str(eintrag[6]) + "\n")  # 6: Einheit
                fobj.write(str(eintrag[7]) + "\n")  # 7: Plot-Fenster: 0= keins, 1= F1, 2=F2
                fobj.write(str(eintrag[8]) + "\n")  # 8: linestyle
                fobj.write(str(eintrag[9]) + "\n")  # 9: linewidth
                fobj.write(str(eintrag[10]) + "\n")  # 10: marker
                fobj.write(str(eintrag[11]) + "\n")  # 11: markerwidth
                fobj.write(str(eintrag[12]) + "\n")  # 12: comments
                fobj.write("</start>\n")
        else:
            return

    def load_simplo_format(self):
        self.datenbank = []

        f1 = QFileDialog.getOpenFileName(self, "Load SimPlo File", "",
                                         "SimPlo File (*.spl);;All Files (*)")

        try:
            fobj = open(f1[0], "r")
            ds = []
            data = []
            region = 0
            for li in fobj:

                line = li.rstrip("\n")

                if line == "<start>":
                    data = []
                    region = 0
                    continue

                if region <= 1:
                    data.append(line)
                    region = region + 1

                if line == "<data>":
                    region = 3
                    continue

                if line == "</data>":
                    data.append(np.array(ds))
                    ds = []
                    region = 4
                    continue

                if region == 3:

                    if line == "None":
                        ds.append(None)
                    else:
                        ds.append(float(line))

                if line == "</start>":
                    self.datenbank.append(data)
                    continue

                if region == 4:
                    data.append(line)

            # str umwandeln
            for eintrag in self.datenbank:
                eintrag[4] = int(eintrag[4])
                eintrag[7] = int(eintrag[7])
                eintrag[9] = float(eintrag[9])
                eintrag[11] = float(eintrag[11])

            self.tree_creation_new()
        except:
            return

    def import_csv(self):
        f1 = QFileDialog.getOpenFileName(self, "Load CSV File", "", "CSV File (*.csv);;All Files (*)")
        dateiname = f1[0].split("/")[-1]
        dateiendung = dateiname.split(".")[-1]

        if dateiendung == "csv" or dateiendung == "CSV":

            # wurde die Datei bereit eingelesen?
            for db_eintrag in self.datenbank:
                if dateiname == db_eintrag[0]:
                    QMessageBox.about(self, "Filename already exist!",
                                      "It looks like you've already read this file:\n" + dateiname)
                    return

            trennzeichen = ";"

            # erzeuge eine Matrix zur Identifikation des Datenaufbaus
            anz = []
            fobj = open(f1[0], "r")
            for zeile in fobj:
                anz.append([zeile.count(trennzeichen), zeile.count(","), zeile.count(".")])
            fobj.close()
            anza = np.array(anz)

            # Dezimaltrennzeichen - Behandlung
            komma = False
            komma_punkt = np.array([anza[:, 1].sum(), anza[:, 2].sum()])
            if komma_punkt.sum() != 0:
                if komma_punkt.min() / komma_punkt.max() <= 0.1:
                    # Ein Vergleich der Summe der potentiel gefundenen Dezimal- oder Komma-Trennzeichen, sollte
                    # einen sehr unterschiedlichen Wert ergeben. Aktuelle Einstellung: der kleinere Wert
                    # beträgt 10% (0.1) des größeren.
                    if komma_punkt[0] > komma_punkt[1]:
                        komma = True
                    else:
                        komma = False
                else:
                    QMessageBox.about(self, "Error!",
                                      "The decimal separator could not be clearly identified.\n" +
                                      "\nCheck the file: " + dateiname)
                    return

            a = []
            z_pos = 0
            kopfzeilen = []
            fobj = open(f1[0], "r")
            for zeile in fobj:
                float_zeilenwerte = []
                z_pos = z_pos + 1
                if komma:
                    zeilenwerte = zeile.rstrip().replace(",", ".").split(trennzeichen)  # Einlesen mit Dezimalkomma
                else:
                    zeilenwerte = zeile.rstrip().split(trennzeichen)  # Einlesen mit Dezimalpunkt
                # handelt es sich um Zahlenwerte?
                fehler = []
                c = 0
                no_number = -1
                moeglicher_zeilenfehler = False
                for z in zeilenwerte:
                    c = c + 1
                    try:
                        float_zeilenwerte.append(float(z))
                    except:
                        no_number = no_number + 1
                        if z != "":
                            fehler.append([c, z])

                            moeglicher_zeilenfehler = True
                        else:
                            float_zeilenwerte.append(np.nan)

                if moeglicher_zeilenfehler:
                    if no_number >= round(anza[z_pos - 1, 0] / 2):
                        kopfzeilen.append(zeilenwerte)
                    else:
                        QMessageBox.about(self, "Error!",
                                          "The data in line " + str(z_pos) + " is not a number.\n" +
                                          "[Column, Data]\n" + str(fehler) +
                                          "\nCheck the file: " + dateiname)
                        return
                else:
                    a.append(float_zeilenwerte)
            fobj.close()

            # erzeugt ein numpy array einer Liste von Listen mit unterschiedlicher Listenlänge
            # hierzu werden die "Lücken" mit None gefüllt.
            # Eine Transponierung der Matrix ist anschließend möglich
            length = len(sorted(a, key=len, reverse=True)[0])
            a_np = np.array([xi + [None] * (length - len(xi)) for xi in a])
            a_np_t = a_np.transpose()

            anz_kopfzeilen = len(kopfzeilen)

            legend_list = []

            # Einlesen der Einheiten-Liste
            unitlist = []
            try:
                file = open("unitlist.dat", "r")
                for zeile in file:
                    unitlist.append(zeile.rstrip())
                file.close()
            except:
                unitlist = ["m", "mbar", "l", "km/h", "nm", "µm", "mm", "m/s", "bar", "ms", "s"]
                QMessageBox.about(self, "Error!",
                                  "The file 'unitlist.dat' could not be read. Check the existence\n" +
                                  "of the file and the entries with a text editor.\n" +
                                  "The units are entered line by line and can be extended.\n" +
                                  "A simple list will be used.")

            # wenn kein Kopf vorhanden ist
            if anz_kopfzeilen == 0:
                for i in range(length):
                    legend_list.append("C" + str(i))
                units_list = ["*"] * (length)

            # Überprüfung der beiden LETZTEN Kopfzeilen oberhalb der Daten auf Konsistenz
            if anz_kopfzeilen >= 1 and anz_kopfzeilen <= 2:

                for h in range(anz_kopfzeilen):

                    if length != len(kopfzeilen[-1 - h]):
                        QMessageBox.about(self, "Error!",
                                          "The number of header entries does not match the number of columns\n" +
                                          "at line: " + str(anz_kopfzeilen - h) +
                                          "\nCheck the file: " + dateiname)
                        return
            # wenn nur eine Kopfzeile vorhanden ist, wir diese für die Legende verwendet
            if anz_kopfzeilen == 1:
                legend_list = kopfzeilen[0]
                units_list = ["*"] * (length)

            # wenn mindestens zwei Kopfzeilen verwendet werden, wird überprüft ob in der letzten Zeile
            # oberhalb der Daten Einheiten stehen
            if anz_kopfzeilen >= 2:
                unerwuenschtes = "[] "
                units_list = []
                for eintrag in kopfzeilen[-1]:  # Einheiten-Check
                    rest_liste = []
                    eintrag_ohne_unerwuenschtes = eintrag
                    for unit in unitlist:
                        for unerw in unerwuenschtes:
                            eintrag_ohne_unerwuenschtes = eintrag_ohne_unerwuenschtes.replace(unerw, "")
                        rest_liste.append(len(eintrag_ohne_unerwuenschtes.replace(unit, "")))
                    min_index = rest_liste.index(min(rest_liste))
                    if min(rest_liste) <= 3:
                        units_list.append(unitlist[min_index])
                    else:
                        units_list.append("*")
                legend_list = kopfzeilen[-2]

            # Füllung leerer legend_list Einträge
            next_ID = self.next_usable_id()

            # laenge_db = len(self.datenbank)
            for ll in range(length):
                if legend_list[ll] == "":
                    legend_list[ll] = "ID: " + str(next_ID + ll)

            # Einlesen in die Datenbank

            for i in range(length):
                self.datenbank.append([dateiname,  # 0: Dateiname
                                       legend_list[i],  # 1: Legende (Kopfzeileneintrag)
                                       a_np_t[i, :],  # 2: Daten
                                       "not defined",  # 3: Achsentyp
                                       next_ID + i,  # 4: ID
                                       "*",  # 5: Connection
                                       units_list[i],  # 6: Einheit
                                       0,  # 7: Plot-Fenster: 0= keins, 1= F1, 2=F2
                                       "-",  # 8: linestyle
                                       1.0,  # 9: linewidth
                                       "o",  # 10: marker
                                       5.0,  # 11: markerwidth
                                       str(legend_list[i]) + "\n" + "-" * 50 + "\n", ])  # 12: comments
                # []])             #

            self.tree_creation_new()
            # self.plotten()

    def export_csv(self):
        lis = self.create_index_list_of_selected_items()
        if len(lis) >= 1:
            rdb = self.find_real_db_id(lis)
            f1 = QFileDialog.getSaveFileName(self, "Export CSV-File", "",
                                             "CSV-File (*.csv);;All Files (*)")
            if f1[0] == "": return

            my_header = ""
            my_units = ""
            A = []
            for i in rdb:
                my_header = my_header + str(self.datenbank[i][1]) + ";"
                my_units = my_units + str(self.datenbank[i][6]) + ";"
                x = self.datenbank[i][2]
                A.append(x.tolist())

            fullheader = my_header[:-1] + "\n" + my_units[:-1]

            length = len(sorted(A, key=len, reverse=True)[0])
            data = np.array([xi + [np.nan] * (length - len(xi)) for xi in A])
            data_T = data.transpose()

            np.savetxt(f1[0], data_T, fmt='%.18e', delimiter=';', newline='\n', header=fullheader, footer='',
                       comments='')

    # tiny helpfull things
    def create_index_list_of_selected_items(self):

        index_list = []
        for eintrag in self.treeWidget.selectedItems():
            if eintrag.parent():
                # gibt es ein Parent-Item zu dem aktuellen Item? Wenn nicht, handelt es sich um ein Child-Item
                # eintrag.setText(1, achsenart)
                index_list.append(int(eintrag.text(2)))
        return index_list

    def find_real_db_id(self, index_list):
        real_db_id = []
        database_length = len(self.datenbank)
        for i in index_list:
            for a in range(database_length):
                if self.datenbank[a][4] == i:
                    real_db_id.append(a)
        return real_db_id

    def next_usable_id(self):
        id_liste = []
        if len(self.datenbank) != 0:
            for eintrag in self.datenbank:
                id_liste.append(eintrag[4])
            max_id = max(id_liste)

        else:
            max_id = -1
        return max_id + 1

    def set_y_length_like_x_length(self,x,y):
        y1 = y.tolist()
        len_x = len(x)
        len_y = len(y)
        differenz = len_x-len_y
        if differenz>0:
            y1.append(np.nan*differenz)

        if differenz<0:
            y1 = y1[:differenz]

        return np.array(y1)


    # math
    def math_operations(self):

        index_list = self.create_index_list_of_selected_items()
        if len(index_list) < 1 or len(index_list) > 2:
            QMessageBox.about(self, "Error!", "Please select only one or two lines!")
            return
        ril = self.find_real_db_id(index_list)

        if len(ril) == 2:
            x_str = str(self.datenbank[ril[0]][1])
            y_str = str(self.datenbank[ril[1]][1])
            x = self.datenbank[ril[0]][2]
            y = self.datenbank[ril[1]][2]
        else:
            x_str = str(self.datenbank[ril[0]][1])
            y_str = "[1]*n"
            x = self.datenbank[ril[0]][2]
            laenge = len(self.datenbank[ril[0]][2])
            y = np.array([1] * laenge)

        item, ok = QInputDialog.getText(self, "Basic Operations (x*y)", "Basic Operations (x*y)\n\n" +
                                        "Selected Data:\n" +
                                        "x = " + x_str + "\n" +
                                        "y = " + y_str + "\n\n" +
                                        "Examples: 'x*y+100','x**y")
        if item == "" and ok == True:
            return
        if ok:

            try:
                z = eval(item)
            except:
                QMessageBox.about(self, "Error!", "Cant't convert input string to math expression!")
                return

            next_ID = self.next_usable_id()
            puffer = copy.deepcopy(self.datenbank[ril[0]])
            self.datenbank.append(puffer)
            self.datenbank[next_ID][0] = "Math: " + item
            self.datenbank[next_ID][1] = "x: " + x_str + "; y: " + y_str
            self.datenbank[next_ID][2] = z
            self.datenbank[next_ID][4] = next_ID
            self.tree_creation_new()

        return

    def diff_proc(self):
        index_list = self.create_index_list_of_selected_items()
        real_index_list = self.find_real_db_id(index_list)
        if len(index_list) != 2:
            QMessageBox.about(self, "Unable to differentiate data!", "Please select no more or less than two lines!")
            return

        item, ok = QInputDialog.getText(self, "Numerical &Differentiation", "Enter folder name:")
        if item == "" and ok == True:
            QMessageBox.about(self, "Error!", "Type valid folder name!")
            return
        if ok:
            copy_index = 0
            xy = [self.datenbank[real_index_list[0]][3], self.datenbank[real_index_list[1]][3]]
            dydx = []

            if xy[0] == "x-axis" and xy[1] == "y-axis":
                x = self.datenbank[real_index_list[0]][2]
                y = self.datenbank[real_index_list[1]][2]
                y = self.set_y_length_like_x_length(x,y)

                dydx = np.diff(y) / np.diff(x)
                copy_index = real_index_list[1]

            if xy[1] == "x-axis" and xy[0] == "y-axis":
                x = self.datenbank[real_index_list[1]][2]
                y = self.datenbank[real_index_list[0]][2]
                y = self.set_y_length_like_x_length(x, y)
                dydx = np.diff(y) / np.diff(x)
                copy_index = real_index_list[0]

            if dydx != []:
                next_ID = self.next_usable_id()
                puffer = copy.deepcopy(self.datenbank[copy_index])
                self.datenbank.append(puffer)
                self.datenbank[next_ID][0] = item
                self.datenbank[next_ID][1] = "dy:" + str(self.datenbank[next_ID][1])
                self.datenbank[next_ID][2] = dydx
                self.datenbank[next_ID][4] = next_ID
                self.tree_creation_new()
        return

    # create the tree
    def tree_creation_new(self):

        self.treeWidget.clear()
        i = 0
        j = 0
        for db_eintrag in self.datenbank:

            try:
                if db_eintrag[0] == self.treeWidget.topLevelItem(i).text(0):
                    # wenn der Dateneintrag aus der gleichen Datei stammt:
                    self.spalten.append(QtWidgets.QTreeWidgetItem(self.elemente[-1]))
                    self.treeWidget.topLevelItem(i).child(j).setText(0, str(db_eintrag[1]))
                    self.treeWidget.topLevelItem(i).child(j).setText(1, str(db_eintrag[3]))
                    self.treeWidget.topLevelItem(i).child(j).setText(2, str(db_eintrag[4]))
                    self.treeWidget.topLevelItem(i).child(j).setText(3, str(db_eintrag[5]))
                    self.treeWidget.topLevelItem(i).child(j).setText(4, str(db_eintrag[6]))
                    self.treeWidget.topLevelItem(i).child(j).setText(5, str(db_eintrag[7]))
                    j = j + 1

                if db_eintrag[0] != self.treeWidget.topLevelItem(i).text(0):
                    # wenn im Vergleich zum zuvor eingelesenen Dateneintrag, der Datensatz aus einer
                    # neuen Datei stammt:
                    j = 0
                    i = i + 1
                    self.elemente.append(QtWidgets.QTreeWidgetItem(self.treeWidget))
                    self.treeWidget.topLevelItem(i).setText(0, db_eintrag[0])
                    self.spalten.append(QtWidgets.QTreeWidgetItem(self.elemente[-1]))
                    self.treeWidget.topLevelItem(i).child(j).setText(0, str(db_eintrag[1]))
                    self.treeWidget.topLevelItem(i).child(j).setText(1, str(db_eintrag[3]))
                    self.treeWidget.topLevelItem(i).child(j).setText(2, str(db_eintrag[4]))
                    self.treeWidget.topLevelItem(i).child(j).setText(3, str(db_eintrag[5]))
                    self.treeWidget.topLevelItem(i).child(j).setText(4, str(db_eintrag[6]))
                    self.treeWidget.topLevelItem(i).child(j).setText(5, str(db_eintrag[7]))
                    j = j + 1
            except:
                # wird durchgeführt wenn noch kein Eintrag verhanden ist (einmaliger Durchlauf)
                self.elemente.append(QtWidgets.QTreeWidgetItem(self.treeWidget))
                self.treeWidget.topLevelItem(i).setText(0, db_eintrag[0])
                self.spalten.append(QtWidgets.QTreeWidgetItem(self.elemente[-1]))
                self.treeWidget.topLevelItem(i).child(j).setText(0, str(db_eintrag[1]))
                self.treeWidget.topLevelItem(i).child(j).setText(1, str(db_eintrag[3]))
                self.treeWidget.topLevelItem(i).child(j).setText(2, str(db_eintrag[4]))
                self.treeWidget.topLevelItem(i).child(j).setText(3, str(db_eintrag[5]))
                self.treeWidget.topLevelItem(i).child(j).setText(4, str(db_eintrag[6]))
                self.treeWidget.topLevelItem(i).child(j).setText(5, str(db_eintrag[7]))
                j = j + 1
        self.treeWidget.expandAll()
        self.treeWidget.setAlternatingRowColors(True)
        for x in range(1,6):
            self.treeWidget.resizeColumnToContents(x)


    # data handling
    def delete_selected_data(self):

        index_list = self.create_index_list_of_selected_items()
        self.remove_connection_number(index_list)
        anz_index = len(index_list)
        if anz_index >= 1:
            real_index = self.find_real_db_id(index_list)
            real_index.sort(reverse=True)
            for i in real_index:
                del self.datenbank[i]
            self.tree_creation_new()

    def duplicate_proc(self):

        index_list = self.create_index_list_of_selected_items()
        anz_index = len(index_list)
        if anz_index >= 1:  #
            item, ok = QInputDialog.getText(self, "Duplicate", str(anz_index) + " selected. Enter folder name:")
        else:
            return

        if item == "" and ok == True:
            QMessageBox.about(self, "Error!", "Type valid folder name!")
            return

        if ok:
            # laenge_db = len(self.datenbank)
            next_ID = self.next_usable_id()

            i = 0
            for ind in index_list:
                puffer = copy.deepcopy(self.datenbank[ind])
                self.datenbank.append(puffer)
                self.datenbank[next_ID + i][0] = item
                self.datenbank[next_ID + i][1] = "Copy of " + self.datenbank[next_ID + i][1]
                self.datenbank[next_ID + i][4] = next_ID + i
                self.datenbank[next_ID + i][5] = "*"
                i = i + 1
            self.tree_creation_new()

        else:
            return

    def connect_the_data(self):

        index_list = self.create_index_list_of_selected_items()
        anz_index = len(index_list)

        if anz_index != 2:
            QMessageBox.about(self, "Unable to connect data!", "Please select no more or less than two lines!")
            return
        else:
            code = ""
            real_index = []
            for i in index_list:
                for a in range(len(self.datenbank)):
                    if self.datenbank[a][4] == i:
                        if self.datenbank[a][3] == "not defined":
                            code = code + "0"
                            real_index.append(a)
                        if self.datenbank[a][3] == "x-axis":
                            code = code + "1"
                            real_index.append(a)
                        if self.datenbank[a][3] == "y-axis":
                            code = code + "2"
                            real_index.append(a)

            bereits_vorhanden = False
            if code == "00" or code == "10" or code == "12" or code == "02":
                self.datenbank[real_index[0]][3] = "x-axis"
                self.datenbank[real_index[1]][3] = "y-axis"
                if self.datenbank[real_index[0]][5] == "*":
                    self.datenbank[real_index[0]][5] = str(self.datenbank[real_index[1]][4])
                else:
                    bereits_connected_ids = self.datenbank[real_index[0]][5].split(";")
                    for e in bereits_connected_ids:
                        if str(self.datenbank[real_index[1]][4]) == e:
                            bereits_vorhanden = True
                    if not bereits_vorhanden:
                        self.datenbank[real_index[0]][5] = str(self.datenbank[real_index[0]][5]) + ";" + str(
                            self.datenbank[real_index[1]][4])
                        self.datenbank[real_index[1]][5] = "*"

            if code == "01" or code == "20" or code == "21":
                self.datenbank[real_index[1]][3] = "x-axis"
                self.datenbank[real_index[0]][3] = "y-axis"
                if self.datenbank[real_index[1]][5] == "*":
                    self.datenbank[real_index[1]][5] = str(self.datenbank[real_index[0]][4])
                else:
                    bereits_connected_ids = self.datenbank[real_index[1]][5].split(";")
                    for e in bereits_connected_ids:
                        if str(self.datenbank[real_index[0]][4]) == e:
                            bereits_vorhanden = True
                    if not bereits_vorhanden:
                        self.datenbank[real_index[1]][5] = str(self.datenbank[real_index[1]][5]) + ";" + str(
                            self.datenbank[real_index[0]][4])
                        self.datenbank[real_index[0]][5] = "*"

            self.tree_creation_new()

    def disconnect_the_data(self):
        die_ids = self.create_index_list_of_selected_items()
        self.remove_connection_number(die_ids)
        real_ids = self.find_real_db_id(die_ids)
        for i in real_ids:
            self.datenbank[i][5] = "*"
        self.tree_creation_new()

    def remove_connection_number(self, die_ids):
        for i in die_ids:
            for data in self.datenbank:
                if data[5] != "*":
                    conn = data[5].split(";")
                    if str(i) in conn:
                        st1 = data[5].replace(str(i), "")
                        st2 = st1.replace(";;", ";")
                        data[5] = st2.rstrip(";").lstrip(";")
                    if data[5] == "": data[5] = "*"

    # define the axis
    def x_achse(self):
        # self.tabWidget.setCurrentIndex(0)
        self.achsen("x-axis")

    def y_achse(self):
        # self.tabWidget.setCurrentIndex(0)
        self.achsen("y-axis")

    def achsen(self, achsenart):

        index_list = self.create_index_list_of_selected_items()
        anz_index = len(index_list)
        if anz_index >= 1:
            for i in index_list:
                for a in range(len(self.datenbank)):
                    if self.datenbank[a][4] == i:
                        self.datenbank[a][3] = achsenart
                        if achsenart == "y-axis":
                            self.datenbank[a][5] = "*"
                        if achsenart == "x-axis":
                            self.remove_connection_number([i])
                        break
            self.tree_creation_new()

    # define the window
    def pl_wi_1(self):

        # self.tabWidget.setCurrentIndex(3)
        self.plot_window_choise(1)

    def pl_wi_2(self):

        # self.tabWidget.setCurrentIndex(4)
        self.plot_window_choise(2)

    def pl_wi_n(self):

        # self.tabWidget.setCurrentIndex(0)
        self.plot_window_choise(0)

    def plot_window_choise(self, choise):

        index_list = self.create_index_list_of_selected_items()
        anz_index = len(index_list)
        if anz_index >= 1:
            for i in index_list:
                for a in range(len(self.datenbank)):
                    if self.datenbank[a][4] == i:
                        self.datenbank[a][7] = choise
                        break
            self.tree_creation_new()

    # tab filling, limits, comments, etc.
    def fill_tab(self):

        tab_index = self.tabWidget.currentIndex()
        if tab_index == 0:
            # Befüllung der Eingabefelder im Tab-Menu

            index_list = self.create_index_list_of_selected_items()
            selected_list_length = len(index_list)
            if selected_list_length == 1:
                for i in index_list:
                    for a in range(len(self.datenbank)):
                        if self.datenbank[a][4] == i:
                            self.lineEdit_legend.setText(str(self.datenbank[a][1]))  # 1: Kopfzeile
                            self.lineEdit_id.setText(str(self.datenbank[a][4]))  # 4: ID
                            self.lineEdit_connection.setText(str(self.datenbank[a][5]))  # 5: Verbindung
                            self.lineEdit_units.setText(str(self.datenbank[a][6]))  # 6: Einheiten
                            self.comboBox_linestyle_w1.setCurrentText(str(self.datenbank[a][8]))  # 8: linestyle
                            self.doubleSpinBox_linewidth_w1.setValue(float(self.datenbank[a][9]))  # 9: linewidth
                            self.comboBox_marker_w1.setCurrentText(str(self.datenbank[a][8]))  # 10: marker
                            self.doubleSpinBox_markersize_w1.setValue(float(self.datenbank[a][11]))  # 11: markerwidth
                            break

        if tab_index == 1:

            data = []
            header = []
            index_list = self.create_index_list_of_selected_items()

            if len(index_list) > 0:
                for i in index_list:
                    for a in range(len(self.datenbank)):
                        if self.datenbank[a][4] == i:
                            header.append(self.datenbank[a][1])
                            data.append(self.datenbank[a][2].tolist())
                            break

                length = len(sorted(data, key=len, reverse=True)[0])
                data_np = np.array([xi + [np.nan] * (length - len(xi)) for xi in data])

                (co, ro) = data_np.shape
                self.tableWidget_data.setColumnCount(co)
                self.tableWidget_data.setRowCount(ro)

                for row in range(ro):
                    for column in range(co):
                        item = QtWidgets.QTableWidgetItem()
                        item.setText(str(data_np[column, row]))
                        self.tableWidget_data.setItem(row, column, item)

                for i in range(co):
                    item = QtWidgets.QTableWidgetItem()
                    item.setText(header[i])
                    self.tableWidget_data.setHorizontalHeaderItem(i, item)

        if tab_index == 2:

            index_list = self.create_index_list_of_selected_items()
            if len(index_list) == 1:
                ril = self.find_real_db_id(index_list)
                self.plainTextEdit_comments.setPlainText(self.datenbank[ril[0]][12])
                self.comment_id = ril[0]
            else:
                return

    def define_limits(self):
        axis_w = []
        w1 = self.lineEdit_axis_limits_w1.text()
        w2 = self.lineEdit_axis_limits_w2.text()
        axis_list = [w1.split(";"), w2.split(";")]
        for eintrag in axis_list:
            vier_werte = []
            if len(eintrag) == 4:
                for wert in eintrag:
                    try:
                        value = float(wert)
                    except:
                        value = None
                    vier_werte.append(value)
                axis_w.append(vier_werte)
            else:
                axis_w.append([None, None, None, None])
        return axis_w

    def logscale_definition(self, axis_w):
        x_limits_f1 = [self.ax[0].get_xlim()[0], self.ax[0].get_xlim()[1]]
        y_limits_f1 = [self.ax[0].get_ylim()[0], self.ax[0].get_ylim()[1]]
        x_limits_f2 = [self.ax[1].get_xlim()[0], self.ax[1].get_xlim()[1]]
        y_limits_f2 = [self.ax[1].get_ylim()[0], self.ax[1].get_ylim()[1]]
        w1 = self.lineEdit_axis_limits_w1.text()
        w2 = self.lineEdit_axis_limits_w2.text()

        if self.checkBox_logx1.isChecked():
            for i in range(2):
                if axis_w[0][i] == None:
                    if x_limits_f1[i] <= 0.0:
                        self.logscale_def_error(x_limits_f1[i])
                        self.checkBox_logx1.setChecked(False)
                else:
                    if axis_w[0][i] <= 0.0:
                        self.logscale_def_error(axis_w[0][i])
                        self.checkBox_logx1.setChecked(False)

        if self.checkBox_logy1.isChecked():
            for i in range(2):
                if axis_w[0][i + 2] == None:
                    if y_limits_f1[i] <= 0.0:
                        self.logscale_def_error(y_limits_f1[i])
                        self.checkBox_logy1.setChecked(False)
                else:
                    if axis_w[0][i + 2] <= 0.0:
                        self.logscale_def_error(axis_w[0][i + 2])
                        self.checkBox_logy1.setChecked(False)

        if self.checkBox_logx1.isChecked(): self.ax[0].set_xscale('log')
        if self.checkBox_logy1.isChecked(): self.ax[0].set_yscale('log')

        if self.checkBox_logx2.isChecked():
            for i in range(2):
                if axis_w[1][i] == None:
                    if x_limits_f2[i] <= 0.0:
                        self.logscale_def_error(x_limits_f2[i])
                        self.checkBox_logx2.setChecked(False)
                else:
                    if axis_w[1][i] <= 0.0:
                        self.logscale_def_error(axis_w[1][i])
                        self.checkBox_logx2.setChecked(False)

        if self.checkBox_logy2.isChecked():
            for i in range(2):
                if axis_w[1][i + 2] == None:
                    if y_limits_f2[i] <= 0.0:
                        self.logscale_def_error(y_limits_f2[i])
                        self.checkBox_logy2.setChecked(False)
                else:
                    if axis_w[1][i + 2] <= 0.0:
                        self.logscale_def_error(axis_w[1][i + 2])
                        self.checkBox_logy2.setChecked(False)

        if self.checkBox_logx2.isChecked(): self.ax[1].set_xscale('log')
        if self.checkBox_logy2.isChecked(): self.ax[1].set_yscale('log')

    def logscale_def_error(self, fehlerquelle):
        QMessageBox.about(self, "Error!",
                          "Only positive values can be displayed in a logarithmic scale.\n" + str(fehlerquelle))

    def change_comments(self):
        index_list = self.create_index_list_of_selected_items()
        if len(index_list) == 1:
            self.comment = self.plainTextEdit_comments.toPlainText()

    def save_comment_to_db(self):
        index_list = self.create_index_list_of_selected_items()
        if len(index_list) == 1:
            rdi = self.find_real_db_id(index_list)
            self.datenbank[rdi[0]][12] = self.comment
            self.plainTextEdit_comments.setPlainText(self.datenbank[rdi[0]][12])

    def change_lineproperties_in_db(self):

        index_list = self.create_index_list_of_selected_items()
        anz_index = len(index_list)
        if anz_index >= 1:
            for i in index_list:
                for a in range(len(self.datenbank)):
                    if self.datenbank[a][4] == i:
                        self.datenbank[a][8] = self.comboBox_linestyle_w1.currentText()
                        self.datenbank[a][9] = float(self.doubleSpinBox_linewidth_w1.value())
                        self.datenbank[a][10] = self.comboBox_marker_w1.currentText()
                        self.datenbank[a][11] = float(self.doubleSpinBox_markersize_w1.value())
                        break
                        # self.treeWidget.clearSelection()

    def change_legend_in_db(self):
        db_position = int(self.lineEdit_id.text())
        self.datenbank[db_position][1] = self.lineEdit_legend.text()
        self.tree_creation_new()

    def change_unit_in_db(self):
        db_position = int(self.lineEdit_id.text())
        self.datenbank[db_position][6] = self.lineEdit_units.text()
        self.tree_creation_new()

    # plot
    def plot_interpolation(self, x, y):
        # not in use
        f = InterpolatedUnivariateSpline(x, y, k=2)
        yi = f(x)
        return yi

    def check_xy_compa(self, x, y):

        ro_xy = [x.shape[0], y.shape[0]]
        diff = abs(ro_xy[0] - ro_xy[1])
        if diff != 0:
            none_list = []
            for i in range(diff):
                none_list.append(np.nan)
            i_min = ro_xy.index(min(ro_xy))
            if i_min == 0:
                x = np.append(x, none_list)
            else:
                y = np.append(y, none_list)
            return x, y
        else:
            return x, y

    def start_plot(self):
        self.plot(0,"")

    def plot(self,mode,plot_filename):

        # limits
        axis_w = self.define_limits()
        x_label_list = [self.lineEdit_xlabel_w1.text(), self.lineEdit_xlabel_w2.text()]
        y_label_list = [self.lineEdit_ylabel_w1.text(), self.lineEdit_ylabel_w2.text()]
        window_title = [self.lineEdit_title_w1.text(), self.lineEdit_title_w2.text()]

        # Plotten der Daten
        self.ax[0].clear()  # Fenster 1
        self.ax[1].clear()  # Fenster 2
        self.ax[0].patch.set_visible(False)
        for eintrag in self.datenbank:
            if eintrag[7] > 0:  # ist ein Fenster ausgewählt?
                fenster = eintrag[7] - 1  # ax[0] == 1 ; ax[1] == 2
                if eintrag[5] != "*":  # Durchlauf fü xy-plots
                    if eintrag[3] == "x-axis":  # Durchlauf erfolgt nur mit der x-Achse
                        die_ys = [int(a) for a in eintrag[5].split(";")]
                        real_ys_ID = self.find_real_db_id(die_ys)
                        for i in real_ys_ID:
                            x = eintrag[2]
                            y = self.datenbank[i][2]
                            (x, y) = self.check_xy_compa(x, y)
                            unit_x = eintrag[6]
                            unit_y = self.datenbank[i][6]
                            self.ax[fenster].plot(x, y, linestyle=self.datenbank[i][8],
                                                  label=self.datenbank[i][1],
                                                  linewidth=self.datenbank[i][9],
                                                  marker=self.datenbank[i][10],
                                                  markersize=self.datenbank[i][11])
                            self.ax[fenster].grid(color="grey")
                            self.ax[fenster].set_xlabel(x_label_list[fenster] + " [" + unit_x + "]",
                                                        fontsize=self.schrift)
                            self.ax[fenster].set_ylabel(y_label_list[fenster] + " [" + unit_y + "]",
                                                        fontsize=self.schrift)
                            self.ax[fenster].set_title(window_title[fenster])

                else:  # y-plots
                    y = eintrag[2]
                    self.ax[fenster].plot(y, linestyle=eintrag[8],
                                          label=eintrag[1],
                                          linewidth=eintrag[9],
                                          marker=eintrag[10],
                                          markersize=eintrag[11])
                    self.ax[fenster].set_xlabel(x_label_list[fenster], fontsize=self.schrift)
                    self.ax[fenster].set_ylabel(y_label_list[fenster], fontsize=self.schrift)
                    self.ax[fenster].set_title(window_title[fenster])
                self.ax[fenster].axis(axis_w[fenster])
                self.ax[fenster].grid(color="black")
                self.logscale_definition(axis_w)
        #self.ax[0].savefig('test.eps', format='eps', dpi=900)
        self.ax[0].legend(loc='best', fancybox=True, shadow=False, fontsize=self.schrift)
        self.ax[1].legend(loc='best', fancybox=True, shadow=False, fontsize=self.schrift)
        # self.ax[0].set_xlim(0,5)
        # self.ax[1].set_ylim(0,100)

        self.canvas.draw()
        self.canvas2.draw()

        if mode == 1:
            self.figure.savefig(str(plot_filename))
        if mode == 2:
            self.figure2.savefig(str(plot_filename))

    def save_plot_1(self): self.save_plot(1)

    def save_plot_2(self): self.save_plot(2)

    def save_plot(self,mode):
        f1 = QFileDialog.getSaveFileName(self, "Save Plot of Window "+str(mode), "",
                                         "PNG File (*.png);;SVG File (*.svg);;All Files (*)")
        if f1[0] == "": return
        self.plot(mode,f1[0])
        return



    # exit
    def sigint_handler(self, *args):
        """Handler for the SIGINT signal."""
        sys.stderr.write('\r')
        if QMessageBox.question(None, '', "Are you sure you want to quit?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.No) == QMessageBox.Yes:
            QApplication.quit()





def main():
    app = QApplication(sys.argv)
    form = simPlo()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
