from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QGridLayout
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class CalculatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture and Voice Calculator")
        self.setStyleSheet("background-color: #2b2e4a;")  
        self.setGeometry(50, 50, 1400, 300)  

        # Main Layout
        self.main_layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Gesture and Voice Calculator")
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))  
        self.title_label.setStyleSheet("color: #f4a261; margin-bottom: 10px;")  
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Top Section: Webcam Feed and Result
        self.top_layout = QHBoxLayout()

        # Webcam Feed
        self.webcam_label = QLabel()
        self.webcam_label.setFixedSize(775, 500)  
        self.webcam_label.setStyleSheet("border: 3px solid #457b9d; border-radius: 10px;")  
        self.top_layout.addWidget(self.webcam_label, alignment=Qt.AlignCenter)

        # Result Bar
        self.result_layout = QVBoxLayout()

        # "Result" Label
        self.result_title_label = QLabel("Result")
        self.result_title_label.setFont(QFont("Segoe UI", 32, QFont.Bold))  
        self.result_title_label.setStyleSheet("color: #2a9d8f; margin-bottom: 5px;")  
        self.result_title_label.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(self.result_title_label)

        # Expression Display
        self.expression_label = QLineEdit()
        self.expression_label.setReadOnly(True)
        self.expression_label.setFont(QFont("Consolas", 18))  
        self.expression_label.setAlignment(Qt.AlignCenter)
        self.expression_label.setStyleSheet(
            """
            background-color: #3a3d5a; 
            color: #e9c46a; 
            border: 3px solid #ffb703; 
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 50px;
            transition: border-color 0.3s ease; 
            """ 
            )
        self.result_layout.addWidget(self.expression_label)

        self.top_layout.addLayout(self.result_layout)
        self.main_layout.addLayout(self.top_layout)

        # Bottom Section - Calculator Buttons and Action Buttons
        self.bottom_layout = QHBoxLayout()

        # Calculator Buttons
        self.button_layout = QGridLayout()
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("=", 3, 2), ("+", 3, 3)
        ]
        for text, row, col, rowspan, colspan in [(b[0], b[1], b[2], 1, 1) for b in buttons]:
            button = QPushButton(text)
            button.setFont(QFont("Segoe UI", 14, QFont.Bold))  
            button.setStyleSheet(
                """
                background-color: #264653; 
                color: #e9c46a;  
                border: 2px solid #457b9d;  
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
                """
            )
            button.clicked.connect(lambda checked, t=text: self.button_click(t))
            self.button_layout.addWidget(button, row, col, rowspan, colspan)

        self.bottom_layout.addLayout(self.button_layout)

        # Action Buttons - Clear, Voice and Gestures
        self.action_button_layout = QVBoxLayout()
        self.voice_button = QPushButton("Activate Voice")
        self.voice_button.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.voice_button.setStyleSheet(
            """
            background-color: #e76f51;  
            color: white;
            border: 2px solid #e63946;  
            border-radius: 10px;
            padding: 12px;
            margin: 5px;
            """
        )
        self.gesture_button = QPushButton("Activate Gestures")
        self.gesture_button.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.gesture_button.setStyleSheet(
            """
            background-color: #2196F3;  
            color: #e9c46a; 
            border: 2px solid #2a9d8f;  
            border-radius: 10px;
            padding: 12px;
            margin: 5px;
            """
        )
        self.clear_button = QPushButton("Clear")
        self.clear_button.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.clear_button.setStyleSheet(
            """
            background-color: #e63946;  
            color: white;
            border: 2px solid #c0392b; 
            border-radius: 10px;
            padding: 12px;
            margin: 5px;
            """
        )
        self.action_button_layout.addWidget(self.clear_button)
        self.action_button_layout.addWidget(self.voice_button)
        self.action_button_layout.addWidget(self.gesture_button)

        self.bottom_layout.addLayout(self.action_button_layout)
        self.main_layout.addLayout(self.bottom_layout)

        self.setLayout(self.main_layout)

    def button_click(self, text):
        if text == "Clear":
            self.expression_label.clear()
        elif text == "=":
            try:
                expression = self.expression_label.text()
                result = str(eval(expression))
                self.expression_label.setText(f"{expression} = {result}")
            except Exception:
                self.expression_label.setText("Error")
        else:
            self.expression_label.setText(self.expression_label.text() + text)

    def update_expression(self, expression):
        self.expression_label.setText(expression)

    def update_webcam_feed(self, pixmap):
        self.webcam_label.setPixmap(pixmap)
