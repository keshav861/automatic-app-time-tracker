import sys
import psutil
import pandas as pd
from datetime import datetime
from pynput import mouse, keyboard
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt
import matplotlib.pyplot as plt

class ActivityLog:
    def __init__(self):
        self.logs = []

    def add_log(self, window, duration, status):
        self.logs.append({'window': window, 'duration': duration, 'status': status})

    def get_logs(self):
        return self.logs

    def get_active_window(self):
        if psutil.WINDOWS:
            import win32gui
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        elif psutil.MACOS:
            import subprocess
            script = 'tell application "System Events" to get the name of the first process whose frontmost is true'
            return subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
        else:
            return "Unsupported OS"

class ActivityTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activity Tracker")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #2e3440; color: #eceff4;")
        
        self.active_window = None
        self.start_time = None
        self.activity_log = ActivityLog()

        self.activity_monitor = ActivityMonitor()
        self.mouse_listener, self.keyboard_listener = self.activity_monitor.start()

        self.initUI()
        self.track_time()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.label = QLabel("Activity Tracker Running...", self)
        self.label.setFont(QFont("Arial", 18, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(self.label)
        
        self.button_layout = QHBoxLayout()

        self.log_report_button = self.create_button("Log & Report", "icons/report_icon.png", self.show_report_window)
        self.button_layout.addWidget(self.log_report_button)

        self.realtime_tracker_button = self.create_button("Real-Time Tracker", "icons/tracker_icon.png", self.show_realtime_window)
        self.button_layout.addWidget(self.realtime_tracker_button)
        
        layout.addLayout(self.button_layout)

        self.break_reminder_label = QLabel("", self)
        self.break_reminder_label.setAlignment(Qt.AlignCenter)
        self.break_reminder_label.setFont(QFont("Arial", 12))
        self.break_reminder_label.setStyleSheet("margin-top: 20px;")
        layout.addWidget(self.break_reminder_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.remind_break)
        self.break_timer.start(3600000)  # Remind every hour

    def create_button(self, text, icon_path, callback):
        button = QPushButton(text, self)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: #eceff4;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
        """)
        button.setIcon(QIcon(QPixmap(icon_path)))  # Add your icon path here
        button.clicked.connect(callback)
        return button

    def track_time(self):
        self.active_window = self.activity_log.get_active_window()
        self.start_time = datetime.now()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_time)
        self.update_timer.start(1000)

    def update_time(self):
        new_window = self.activity_log.get_active_window()
        if new_window != self.active_window:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.activity_log.add_log(self.active_window, duration, "Stopped")
            self.active_window = new_window
            self.start_time = datetime.now()
            self.activity_log.add_log(self.active_window, 0, "Running")
        else:
            duration = (datetime.now() - self.start_time).total_seconds()
            for log in self.activity_log.get_logs():
                if log['window'] == self.active_window and log['status'] == "Running":
                    log['duration'] = duration

        self.update_activity_log_table()

    def show_report_window(self):
        if not self.activity_log.get_logs():
            QMessageBox.warning(self, "Log & Report", "No activity to report.")
            return

        report_window = ReportWindow(self.activity_log.get_logs())
        report_window.exec_()

    def show_realtime_window(self):
        self.realtime_window = RealTimeWindow(self)
        self.realtime_window.show()

    def remind_break(self):
        self.break_reminder_label.setText("Time to take a break!")
        QTimer.singleShot(10000, lambda: self.break_reminder_label.setText(""))

    def update_activity_log_table(self):
        if hasattr(self, 'realtime_window') and self.realtime_window.isVisible():
            self.realtime_window.update_table()

    def closeEvent(self, event):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        event.accept()

class ActivityMonitor:
    def __init__(self):
        self.last_activity = datetime.now()

    def on_move(self, x, y):
        self.last_activity = datetime.now()

    def on_click(self, x, y, button, pressed):
        self.last_activity = datetime.now()

    def on_press(self, key):
        self.last_activity = datetime.now()

    def start(self):
        mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        mouse_listener.start()
        keyboard_listener.start()
        return mouse_listener, keyboard_listener

class ReportWindow(QDialog):
    def __init__(self, activity_log):
        super().__init__()
        self.setWindowTitle("Activity Log & Report")
        self.setGeometry(150, 150, 800, 600)
        self.setStyleSheet("background-color: #3b4252; color: #eceff4;")
        self.activity_log = activity_log

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setRowCount(len(self.activity_log))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Application/Website", "Duration (seconds)", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #4c566a;
                color: #eceff4;
                border: 1px solid #5e81ac;
            }
            QHeaderView::section {
                background-color: #5e81ac;
                border: 1px solid #4c566a;
            }
        """)

        for row, log in enumerate(self.activity_log):
            self.table.setItem(row, 0, QTableWidgetItem(log['window']))
            self.table.setItem(row, 1, QTableWidgetItem(str(log['duration'])))
            self.table.setItem(row, 2, QTableWidgetItem(log['status']))

        layout.addWidget(self.table)

        self.download_log_button = self.create_button("Download Log", "icons/download_icon.png", self.download_log)
        layout.addWidget(self.download_log_button)

        self.download_report_button = self.create_button("Download Report", "icons/download_report_icon.png", self.download_report)
        layout.addWidget(self.download_report_button)

        self.setLayout(layout)

    def create_button(self, text, icon_path, callback):
        button = QPushButton(text, self)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: #eceff4;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
        """)
        button.setIcon(QIcon(QPixmap(icon_path)))  # Add your icon path here
        button.clicked.connect(callback)
        return button

    def download_log(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if filepath:
            df = pd.DataFrame(self.activity_log)
            summary = df.groupby('window')['duration'].sum().reset_index()
            summary.sort_values(by='duration', ascending=False, inplace=True)
            with open(filepath, 'w') as file:
                file.write("Detailed Logs\n")
                df.to_csv(file, index=False)
                file.write("\nFinal Time Usage Summary\n")
                summary.to_csv(file, index=False)
            QMessageBox.information(self, "Save Log", f"Log saved to {filepath}")

    def download_report(self):
        if not self.activity_log:
            QMessageBox.warning(self, "Generate Report", "No activity to report.")
            return

        df = pd.DataFrame(self.activity_log)
        summary = df.groupby('window')['duration'].sum().reset_index()
        summary.sort_values(by='duration', ascending=False, inplace=True)

        plt.figure(figsize=(10, 5))
        plt.bar(summary['window'], summary['duration'])
        plt.xlabel('Applications/Websites')
        plt.ylabel('Time Spent (seconds)')
        plt.title('Time Usage Report')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        options = QFileDialog.Options()
        report_filepath, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "PNG Files (*.png);;All Files (*)", options=options)
        if report_filepath:
            plt.savefig(report_filepath)
            plt.close()
            QMessageBox.information(self, "Generate Report", f"Report saved to {report_filepath}")

class RealTimeWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Real-Time Activity Tracker")
        self.setGeometry(150, 150, 800, 600)
        self.setStyleSheet("background-color: #3b4252; color: #eceff4;")
        self.main_window = main_window

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Application/Website", "Duration (seconds)", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #4c566a;
                color: #eceff4;
                border: 1px solid #5e81ac;
            }
            QHeaderView::section {
                background-color: #5e81ac;
                border: 1px solid #4c566a;
            }
        """)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.download_log_button = QPushButton("Download Log", self)
        self.download_log_button.setFont(QFont("Arial", 12))
        self.download_log_button.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: #eceff4;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
        """)
        self.download_log_button.setIcon(QIcon(QPixmap("icons/download_icon.png")))  # Add your icon path here
        self.download_log_button.clicked.connect(self.download_log)
        button_layout.addWidget(self.download_log_button)

        self.download_report_button = QPushButton("Download Report", self)
        self.download_report_button.setFont(QFont("Arial", 12))
        self.download_report_button.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: #eceff4;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
        """)
        self.download_report_button.setIcon(QIcon(QPixmap("icons/download_report_icon.png")))  # Add your icon path here
        self.download_report_button.clicked.connect(self.download_report)
        button_layout.addWidget(self.download_report_button)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_table)
        self.update_timer.start(1000)

    def update_table(self):
        activity_log = self.main_window.activity_log.get_logs()
        df = pd.DataFrame(activity_log)
    
    # Aggregate time usage by application/website
        summary = df.groupby('window')['duration'].sum().reset_index()
        summary.sort_values(by='duration', ascending=False, inplace=True)
    
        self.table.setRowCount(len(summary))
        for row, log in enumerate(summary.itertuples(index=False)):
            self.table.setItem(row, 0, QTableWidgetItem(log.window))
            self.table.setItem(row, 1, QTableWidgetItem(str(log.duration)))
            self.table.setItem(row, 2, QTableWidgetItem("Running"))  # Or other status if needed


    def download_log(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if filepath:
            df = pd.DataFrame(self.main_window.activity_log.get_logs())
        
        # Aggregating time usage by application/website
            summary = df.groupby('window')['duration'].sum().reset_index()
            summary.sort_values(by='duration', ascending=False, inplace=True)
        
        # Save detailed log and summary to CSV
            with open(filepath, 'w') as file:
                file.write("Detailed Logs\n")
                df.to_csv(file, index=False)
                file.write("\nFinal Time Usage Summary\n")
                summary.to_csv(file, index=False)
        
            QMessageBox.information(self, "Save Log", f"Log saved to {filepath}")


    def download_report(self):
        if not self.main_window.activity_log.get_logs():
            QMessageBox.warning(self, "Generate Report", "No activity to report.")
            return

        df = pd.DataFrame(self.main_window.activity_log.get_logs())
    
    # Aggregate time usage by application/website
        summary = df.groupby('window')['duration'].sum().reset_index()
        summary.sort_values(by='duration', ascending=False, inplace=True)

    # Plotting
        plt.figure(figsize=(10, 5))
        plt.bar(summary['window'], summary['duration'])
        plt.xlabel('Applications/Websites')
        plt.ylabel('Time Spent (seconds)')
        plt.title('Time Usage Report')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        options = QFileDialog.Options()
        report_filepath, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "PNG Files (*.png);;All Files (*)", options=options)
        if report_filepath:
            plt.savefig(report_filepath)
            plt.close()
            QMessageBox.information(self, "Generate Report", f"Report saved to {report_filepath}")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    tracker = ActivityTracker()
    tracker.show()
    sys.exit(app.exec_())
