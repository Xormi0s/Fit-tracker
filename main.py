from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDateEdit, QLineEdit
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sys import exit

class FitTrack(QWidget):
    def __init__(self):
        super().__init__()
        self.settings()
        self.initUI()
        
    def settings(self):
        self.setWindowTitle("FitTracker")
        self.resize(800, 700)
        
    def initUI(self):
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())

        self.cal_box = QLineEdit()
        self.cal_box.setPlaceholderText("Number of burned calories")
        
        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("Enter distance ran")
         
        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter a description")
        
        self.submit_btn = QPushButton("Submit")
        self.add_btn = QPushButton("Add")
        self.delete_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")
        self.dark_mode = QCheckBox("Dark Mode")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Calories", "Distance", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.master_layout = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()
        
        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()
        
        self.sub_row1.addWidget(QLabel("Date:"))
        self.sub_row1.addWidget(self.date_box)
        self.sub_row2.addWidget(QLabel("Calories:"))
        self.sub_row2.addWidget(self.cal_box)
        self.sub_row3.addWidget(QLabel("Distance:"))
        self.sub_row3.addWidget(self.distance_box)
        self.sub_row4.addWidget(QLabel("Description:"))
        self.sub_row4.addWidget(self.description)

        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)
        self.col1.addWidget(self.dark_mode)
        
        self.btn_row1 = QHBoxLayout()
        self.btn_row2 = QHBoxLayout()
        
        self.btn_row1.addWidget(self.add_btn)
        self.btn_row1.addWidget(self.delete_btn)
        self.btn_row2.addWidget(self.submit_btn)
        self.btn_row2.addWidget(self.clear_btn)
        
        self.col1.addLayout(self.btn_row1)
        self.col1.addLayout(self.btn_row2)
        
        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)
        
        
        self.master_layout.addLayout(self.col1, 30)
        self.master_layout.addLayout(self.col2, 70)
        self.setLayout(self.master_layout)

        self.load_table()
        self.button_click()
        self.apply_styles()
        
    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fitness ORDER BY date DESC")
        row = 0
        while query.next():
            id = query.value(0)
            date = query.value(1)
            calories = query.value(2)
            distance = query.value(3)
            description = query.value(4)

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(str(calories)))
            self.table.setItem(row, 3, QTableWidgetItem(str(distance)))
            self.table.setItem(row, 4, QTableWidgetItem(description))
            row += 1

    def button_click(self):
        self.add_btn.clicked.connect(self.add_workout)
        self.delete_btn.clicked.connect(self.delete_workout)
        self.submit_btn.clicked.connect(self.calc_calories)
        self.clear_btn.clicked.connect(self.reset)
        self.dark_mode.stateChanged.connect(self.toggle_dark_mode)

    def add_workout(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        calories = self.cal_box.text()
        distance = self.distance_box.text()
        description = self.description.text()

        query = QSqlQuery("""
            INSERT INTO fitness (date, calories, distance, description)
            VALUES (?, ?, ?, ?)
        """)
        query.addBindValue(date)
        query.addBindValue(calories)
        query.addBindValue(distance)
        query.addBindValue(description)
        query.exec_()

        self.date_box.setDate(QDate.currentDate())
        self.cal_box.clear()
        self.distance_box.clear()
        self.description.clear()

        self.load_table()

    def delete_workout(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please chose a row to delete!")
            return

        id = int(self.table.item(selected_row, 0).text())
        confirm = QMessageBox.question(self, "Are you sure?", "Delete this workout?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM fitness WHERE ID = ?")
        query.addBindValue(id)
        query.exec_()

        self.load_table()

    def calc_calories(self):
        distances = []
        calories = []

        query = QSqlQuery("SELECT distance, calories FROM fitness ORDER BY calories ASC")
        while query.next():
            distance = query.value(0)
            calorie = query.value(1)
            distances.append(distance)
            calories.append(calorie)

        try:
            min_calorie = min(calories)
            max_calorie = max(calories)
            normalized_calories = [(calorie - min_calorie) / (max_calorie - min_calorie) for calorie in calories]

            plt.style.use("Solarize_Light2")
            ax = self.figure.subplots()
            ax.scatter(distances, calories, c = normalized_calories, cmap="Dark2", label="Data Points")
            ax.set_title("Distance Vs. Calories")
            ax.set_xlabel("Distance")
            ax.set_ylabel("Calories")
            cbar = ax.figure.colorbar(ax.collections[0], label="Normalized Calories")
            ax.legend()
            self.canvas.draw()

        except Exception as e:
            print(f"Error:{e}")
            QMessageBox.warning(self, "Error", "Please enter some data first!")

    def apply_styles(self):
        self.setStyleSheet("""
                    QWidget {
                        background-color: #b8c9e1;
                    }

                    QLabel {
                        color: #333;
                        font-size: 14px;
                    }

                    QLineEdit, QComboBox, QDateEdit, QPushButton {
                        background-color: #b8c9e1;
                        color: #333;
                        border: 1px solid #444;
                        padding: 5px;
                    }

                    QTableWidget {
                        background-color: #b8c9e1;
                        color: #333;
                        border: 1px solid #444;
                        selection-background-color: #ddd;
                    }

                    QPushButton {
                        background-color: #4caf50;
                        color: #fff;
                        border: none;
                        padding: 8px 16px;
                        font-size: 14px;
                    }

                    QPushButton:hover {
                        background-color: #45a049;
                    }


                """)
        figure_color = "#b8c9e1"
        self.figure.patch.set_facecolor(figure_color)
        self.canvas.setStyleSheet(f"background-color: {figure_color};")

        if self.dark_mode.isChecked():
            self.setStyleSheet(
                """
                FitnessApp {
                    background-color: #222222;
                }

                QLineEdit, QPushButton, QDateEdit {
                    background-color:#222222;
                    color: #eeeeee;
                    border: 1px solid #444;
                    padding: 5px;
                }
                QLabel{
                     background-color:#222222;
                    color: #eeeeee;
                    padding: 5px;
                }

                QTableWidget {
                    background-color: #444444;
                    color: #eeeeee;
                }

                QCheckBox{
                    color: #eeeeee;
                }
                QPushButton {
                background-color: #40484c;
                color: #fff;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }

                QPushButton:hover {
                    background-color: #444d4f;
                }
                """
            )
            figure_color = "#222222"
            self.figure.patch.set_facecolor(figure_color)
            self.canvas.setStyleSheet(f"background-color: {figure_color};")

    def toggle_dark_mode(self):
        self.apply_styles()

    def reset(self):
        self.date_box.setDate(QDate.currentDate())
        self.description.clear()
        self.cal_box.clear()
        self.distance_box.clear()
        self.figure.clear()
        self.canvas.draw()


db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("fitness.db")

if not db.open():
    QMessageBox.critical(None, "Error", "Cannot open the Database!!!")        
    exit(2)
    
query = QSqlQuery()
query.exec_("""
            CREATE TABLE IF NOT EXISTS fitness (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                calories REAL,
                distance REAL,
                description TEXT
            )
            """)
        
if __name__ == "__main__":
    app = QApplication([])
    main = FitTrack()
    main.show()
    app.exec()