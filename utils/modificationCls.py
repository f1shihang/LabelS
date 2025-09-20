import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QInputDialog, \
    QDesktopWidget
import yaml
from common_fun import root

root = root.parent


class modificationCls(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置主窗口属性
        self.setGeometry(300, 300, 300, 400)
        # 显示到屏幕中心
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        self.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)

        self.setWindowTitle('cls')

        # 设置全局样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #5cacf2; 
                border: 1px solid #3c8ad8; 
                padding: 5px 15px; 
                color: white;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #3c8ad8;
            }

            QListWidget {
                border: 1px solid #5cacf2;
                background-color: #f0f0f0;
            }

            QListWidget::item:selected {
                background-color: #5cacf2;
                color: white;
            }
        """)

        # 创建 QWidget 和 QVBoxLayout 作为主窗口的中心部件和布局
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # 创建 QListWidget
        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)
        with open(root / 'Detection.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        self.names = data['names']

        # 为 QListWidget 添加示例条目
        for i, j in self.names.items():
            self.listWidget.addItem(j)

        # 创建三个按钮并连接到相关函数
        self.btnAdd = QPushButton("添加")
        self.btnAdd.clicked.connect(self.addItem)
        layout.addWidget(self.btnAdd)

        self.btnModify = QPushButton("修改选中")
        self.btnModify.clicked.connect(self.modifyItem)
        layout.addWidget(self.btnModify)

        self.btnDelete = QPushButton("删除选中")
        self.btnDelete.clicked.connect(self.deleteItem)
        layout.addWidget(self.btnDelete)

        self.show()

    def addItem(self):
        name, ok = QInputDialog.getText(self, '输入框', '请输入新增类别名:')
        if name not in self.names.values() and ok:
            with open(root / 'Detection.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                data['names'][len(data['names'])] = name
            with open(root / 'Detection.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True)
            self.initUI()

    def modifyItem(self):
        current_item = self.listWidget.currentItem()
        if current_item:
            name, ok = QInputDialog.getText(self, '输入框', '请输入新类名:')
            if ok and name not in self.names.values():
                current_item.setText(f'{name}')
                with open(root / 'Detection.yaml', 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                    t = data['names']
                    t[self.listWidget.currentRow()] = name
                    data['names'] = t
                with open(root / 'Detection.yaml', 'w', encoding='utf-8') as file:
                    yaml.dump(data, file, allow_unicode=True)

    def deleteItem(self):
        current_row = self.listWidget.currentRow()
        if current_row != -1:  # -1 表示没有选中的条目
            self.listWidget.takeItem(current_row)
            with open(root / 'Detection.yaml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                t = {k: i[1] for k, i in enumerate(data['names'].items()) if k != current_row}
                t = {k: i[1] for k, i in enumerate(t.items())}
                data['names'] = t
            with open(root / 'Detection.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = modificationCls()
    sys.exit(app.exec_())
