from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDateEdit, QLineEdit
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from sys import exit

class FitTrack(QWidget):
    def __init__(self):
        super().__init__()
        
    def initUI(self):
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())

        self.cal_box = QLineEdit()
        self.cal_box.setPlaceholderText("Number of burned calories")
        
        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("Enter distance ran")
         
        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter a description")
        

