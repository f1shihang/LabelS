import os
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox
from utils import MainWin, root

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if len(os.listdir(root / 'temp_folder')):
        reply = QMessageBox.question(None, '删除确认', '是否删除上一次标注残留标签?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            list(map(os.remove, [os.path.join(root / 'temp_folder', i) for i in os.listdir(root / 'temp_folder')]))
    window = MainWin()
    window.setWindowTitle('标注工具')
    window.show()
    sys.exit(app.exec_())
