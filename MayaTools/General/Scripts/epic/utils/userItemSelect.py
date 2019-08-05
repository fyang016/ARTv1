
from PySide.QtGui import *

class UserSelectItem(QDialog):
    def __init__(self, items, title='Select Node', message='Enter message to user here.', comboSelection=None, parent=None):
        super(UserSelectItem, self).__init__(parent)
        
        self.setWindowTitle(title)
        
        self.result = None
        self.items = items

        self.nodes = QComboBox()
        self.select = QPushButton('SELECT')
        self.cancel = QPushButton('CANCEL')
        self.message = QLabel(message)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.message)
        layout = QHBoxLayout()
        layout.addWidget(self.nodes)
        layout.addWidget(self.select)
        layout.addWidget(self.cancel)
        mainLayout.addLayout(layout)
        self.setLayout(mainLayout)
        
        #connect UI
        self.select.clicked.connect(self.returnSelected)
        self.cancel.clicked.connect(self.returnCancel)

        #add nodes
        if self.items:
            for item in self.items:
                self.nodes.addItem(item)
            if comboSelection:
                if comboSelection in self.items:
                    self.nodes.setCurrentIndex(self.nodes.findText(comboSelection))


        else:
            print 'UserSelectItem>>> Requires item list, got none.'
        
    def returnSelected(self):
        self.result = self.nodes.currentText()
        self.close()
    
    def returnCancel(self):
        self.close()
        
        
def show(items, title='Select Item', message='Enter message to user here.', comboSelection=None):
    getItem = UserSelectItem(items, title=title, message=message, comboSelection=comboSelection)
    getItem.exec_()
    return getItem.result
