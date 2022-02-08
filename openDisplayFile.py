import os

import PySide2
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFileDialog, QApplication, QLineEdit, QPlainTextEdit
from PySide2.QtCore import Signal, Slot

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.btn_dialog = QPushButton('打开文件')
        self.btn_dialog.clicked.connect(self.openFileDialog)
        self.display = QPlainTextEdit()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.btn_dialog)
        self.layout.addWidget(self.display)
        self.setLayout(self.layout)

    @Slot()
    def openFileDialog(self):
        # 生成文件对话框对象
        dialog = QFileDialog()
        # 设置文件过滤器，这里是任何文件，包括目录噢
        dialog.setFileMode(QFileDialog.AnyFile)
        # 设置显示文件的模式，这里是详细模式
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            filepath = fileNames[0]
            data = ''
            with open(filepath, 'r') as f:
                data = f.readlines()
                display_data = ''.join(data)
                print(display_data)
            self.display.setPlaceholderText(display_data)


app = QApplication()
widget = MyWidget()
widget.show()
app.exec_()