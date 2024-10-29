import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QVBoxLayout, QTextEdit, QPushButton
from ui_form import Ui_MainWindow
from views import generate_view
from controllers import generate_code
from generate_access import g_access
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 绑定信号槽
        self.ui.pushButton.clicked.connect(self.on_generate_view_clicked)
        self.ui.pushButton_2.clicked.connect(self.on_generate_controller_clicked)
        self.ui.pushButton_3.clicked.connect(self.on_generate_access_clicked)


    # 生成视图按钮
    def on_generate_view_clicked(self):
        # 获取textEdit中的文本
        model_str = self.ui.textEdit.toPlainText()
        # 获取lineEdit中的文本
        model_name = self.ui.lineEdit.text()
        # 获取lineEdit_2中的文本
        view_name = self.ui.lineEdit_2.text()
        # 调用生成视图函数
        text = generate_view(model_name,view_name,model_str)

        # 显示在子窗口中
        self.show_text_dialog(text)

    def show_text_dialog(self, text):
        dialog = QDialog(self)
        dialog.setWindowTitle("生成的视图")
        dialog.setFixedSize(600, 400)  # 设置固定大小（宽600，高400）

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit(dialog)
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)  # 只读
        layout.addWidget(text_edit)

        # 复制按钮
        copy_button = QPushButton("复制", dialog)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(text))
        layout.addWidget(copy_button)

        # 关闭按钮
        close_button = QPushButton("关闭", dialog)
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()  # 显示对话框

    def copy_to_clipboard(self, text):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)


    # 生成控制层代码
    def on_generate_controller_clicked(self):
        # 获取textEdit_2中的文本
        class_name = self.ui.lineEdit_3.text()
        # 获取lineEdit_3中的文本
        model_name = self.ui.lineEdit_4.text()
        # 调用生成控制层函数
        text = generate_code(class_name, model_name)
        # 显示在子窗口中
        self.show_text_dialog(text)

    # 生成权限配置
    def on_generate_access_clicked(self):
        # 获取textEdit_5中的文本
        model_name = self.ui.lineEdit_5.text()
        str_list = model_name.split()
        text = g_access(str_list)
        # 显示在子窗口中
        self.show_text_dialog(text)







def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
