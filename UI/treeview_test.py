import sys
from PyQt5.QtGui import QIcon

from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
                          QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit, QTreeView, QVBoxLayout,
                             QWidget, QTreeWidget, QTreeWidgetItem, QPushButton)

import pymongo as mng


class App(QWidget):
    PATIENT, SUBJECT, DATE = range(3)

    def __init__(self):
        super().__init__()
        self.title = 'Prototype Data Finder'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 240
        self.initUI()

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.dataGroupBox = QGroupBox("Quon Prostate Project")
        self.treeWidget = QTreeWidget()

        pybutton = QPushButton('Click me', self)
        pybutton.clicked.connect(self.clickMethod)
        pybutton.resize(100, 32)
        #pybutton.move(50, 50)

        dataLayout = QHBoxLayout()
        dataLayout.addWidget(self.treeWidget)
        self.dataGroupBox.setLayout(dataLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dataGroupBox)
        self.setLayout(mainLayout)
        self.createDataTree()
        self.show()

    def createDataTree(self):
        db = mng.MongoClient().prostate_actual.patient
        for patient in db.find():
            parent = QTreeWidgetItem(self.treeWidget)
            parent.setText(0, patient['_id'])
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for filter in sorted(patient['filters'].keys()):
                filt_TP = filter + " " + patient['filters'][filter]['tPoint']
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, filt_TP)
                child.setCheckState(0, Qt.Unchecked)

    def clickMethod(self):
        root = self.treeWidget.invisibleRootItem()
        patient_count = root.childCount()
        checked = {}
        for iii in range(patient_count):
            patient = root.child(iii)
            checked_sweeps = []
            filter_count = patient.childCount()

            for jjj in range(filter_count):
                filter = patient.child(jjj)
                #print(child.isSelected())
                if filter.isSelected():
                    checked_sweeps.append(filter.text(0))
            checked[patient.text(0)] = checked_sweeps
        print(checked)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())