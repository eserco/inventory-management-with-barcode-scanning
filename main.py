import os, datetime,time,sys,socket,threading,gc
import query_funcs as mp
import numpy as np
import pyqtgraph as pg
from threading import Thread 
from socketserver import ThreadingMixIn 
from PyQt5 import QtWidgets
from PyQt5.QtCore import QRect, Qt, QEvent, QThread, pyqtSignal
from PyQt5.QtWidgets import (QTabWidget,QTableWidget,QTableWidgetItem,QVBoxLayout,QFormLayout,QLabel,QSystemTrayIcon,
                             QStyle,QLineEdit,QListWidget,QStackedWidget,QWidget,QPushButton,QMainWindow,qApp,
                             QHBoxLayout,QAction)
from PyQt5.QtGui import QIcon, QIntValidator, QFont
from qtmodern import styles, windows
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import *
from qtpy.QtCore import Qt
from ordered_set import OrderedSet


class TCP_server_thread(Thread):
    def __init__(self,window): 
        Thread.__init__(self) 
        self.window=window
        self.HEADER = 8
        self.PORT = 5050
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DC_MESSAGE = "exit"
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.ADDR)
        
    def run(self): 
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        while True:
            global conn,addr
            conn, addr = self.server.accept()
            thread = client_thread(conn,addr,self.window)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    print("[STARTING] server is starting...")
        
class client_thread(Thread): 
    def __init__(self,conn,addr,window):
        Thread.__init__(self)     
        self.window = window
        self.conn = conn
        self.addr = addr
        self.HEADER = 8
        self.PORT = 5050
        self.FORMAT = 'utf-8'
        self.DC_MESSAGE = "exit"
        
    def run(self):
        print(f"[NEW CONNECTION] {self.addr} connected.")
        connected = True
        while connected:
            try:
                msg_length = self.conn.recv(self.HEADER).decode(self.FORMAT)
            except socket.error as error:
                #print(error)
                continue
            if msg_length:
                msg_length = int(msg_length)
                msg = self.conn.recv(msg_length).decode(self.FORMAT)
                if msg == self.DC_MESSAGE:
                    connected = False
                elif msg.find("/WOOD/") >= 0:
                    self.window.st.chat1.append(msg[:-27])
                elif msg.find("/FBRC/") >= 0:
                    self.window.st.chat2.append(msg[:-27])
                elif msg.find("/PACK/") >= 0:
                    self.window.st.chat3.append(msg[:-27])
                print(f"[{self.addr}] {msg}")
                with open("all-barcodes.txt", "a") as f:
                    f.write(msg + "\n")
                    
                # insert any other functions you want to run here..
                #.
                #.
                #......
                
                self.conn.send("Barcode received".encode(self.FORMAT))
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()  
        
 
class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setFixedSize(300, 150)
        self.setWindowTitle("Stock App")
        self.textName = QtWidgets.QLineEdit(self)
        self.textPass = QtWidgets.QLineEdit(self)
        self.textPass.setPlaceholderText("****")
        self.textPass.setEchoMode(QLineEdit.Password)
        self.buttonLogin = QtWidgets.QPushButton('Admin Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        if (self.textName.text() == 'admin' and
            self.textPass.text() == 'admin'):
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Bad user or password')

class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1050, 550)
        self.setWindowTitle("Stock App")
        self.initUI()
        custom_font = QFont("Times", 12)
        QApplication.setFont(custom_font)
        
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
        self.style().standardIcon(QStyle.SP_ComputerIcon))

        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
       

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                event.ignore()
                self.close()
                return

    
    # Override closeEvent, to intercept the window closing event       
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Stock app was minimized to Tray",
            QSystemTrayIcon.Information,msecs=1) 

    def initUI(self):
        self.st = stackedExample()
        exitAct = QAction(QIcon('exit_icon.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)
        self.statusBar()
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)
        self.setCentralWidget(self.st)
        self.show()
        
      
class stackedExample(QWidget):
    def __init__(self):
        super(stackedExample, self).__init__()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.empty_label)
        self.leftlist = QListWidget()
        self.leftlist.setFixedWidth(250)
        x=self.leftlist.insertItem(0, 'Manage Stock Items')
        self.leftlist.insertItem(1, 'Manage Stock Counts')
        self.leftlist.insertItem(2, 'View Barcode Scan Data')
        self.leftlist.insertItem(3, 'View Stock Counts')
        self.leftlist.insertItem(4, 'Graph')
        self.leftlist.setCurrentItem(self.leftlist.item(0))
        
        
        #init tablewidget column headers
        self.item1 = QTableWidgetItem('Supplier Name')
        self.item1.setBackground(QtGui.QColor(0, 0, 0))
        self.item2 = QTableWidgetItem('Category Name')
        self.item2.setBackground(QtGui.QColor(0, 0, 0))
        self.item3 = QTableWidgetItem('Item Code')
        self.item3.setBackground(QtGui.QColor(0, 0, 0))
        self.item4 = QTableWidgetItem('Stock Name')
        self.item4.setBackground(QtGui.QColor(0, 0, 0))
        self.item5 = QTableWidgetItem('Total Value')
        self.item5.setBackground(QtGui.QColor(0, 0, 0))
        self.item6 = QTableWidgetItem('Total Quantity')
        self.item6.setBackground(QtGui.QColor(0, 0, 0))
        self.item7 = QTableWidgetItem('UoM')
        self.item7.setBackground(QtGui.QColor(0, 0, 0))
        self.item8 = QTableWidgetItem('Size')
        self.item8.setBackground(QtGui.QColor(0, 0, 0))
        self.item9 = QTableWidgetItem('Thickness')
        self.item9.setBackground(QtGui.QColor(0, 0, 0))
        self.item10 = QTableWidgetItem('Date')
        self.item10.setBackground(QtGui.QColor(0, 0, 0))
        
        #when we select a different item on the qlistwidget this signal is triggered
        self.leftlist.itemSelectionChanged.connect(self.item_list_listener)
        
        
        self.plot = pg.PlotWidget()
        self.plot.showGrid(x = True, y = False, alpha = 1) 
        
        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack5 = QWidget() 
        self.stack3 = QWidget()
        self.stack4 = QWidget()
   
        self.stack1UI()
        self.stack2UI()
        self.stack5UI()
        self.stack3UI()
        
        
        
        self.View.setColumnCount(10)
        self.View.setColumnWidth(0, 200)
        self.View.setColumnWidth(1, 150)
        self.View.setColumnWidth(3, 300)
        self.View.setColumnWidth(5, 150)
        self.View.setColumnWidth(8, 200)        
        self.View.insertRow(0)
        self.View.setHorizontalHeaderItem(0,self.item1)
        self.View.setHorizontalHeaderItem(1,self.item2)
        self.View.setHorizontalHeaderItem(2,self.item3)
        self.View.setHorizontalHeaderItem(3,self.item4)
        self.View.setHorizontalHeaderItem(4,self.item5)  
        self.View.setHorizontalHeaderItem(5,self.item6)
        self.View.setHorizontalHeaderItem(6,self.item7)
        self.View.setHorizontalHeaderItem(7,self.item8)
        self.View.setHorizontalHeaderItem(8,self.item9)  
        self.View.setHorizontalHeaderItem(9,self.item10)   
        
                
        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack5)
        self.Stack.addWidget(self.stack3)

        
        #init stack4UI after loading all other widgets to load the graph properly
        self.stack4UI(None)        
        self.Stack.addWidget(self.stack4)       
        
 
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.Stack)
        self.setLayout(hbox)
        self.leftlist.currentRowChanged.connect(self.display)
        self.setGeometry(500,350, 200, 200)
        self.setWindowTitle('Stock Management')
        self.show()
        
    ##WIDGET LISTENERS and EVENT HANDLING##
    def item_list_listener(self):
        if self.leftlist.item(0).isSelected():
            self.stock_supplier_name_1.setFocus(True)
        elif self.leftlist.item(1).isSelected():
            self.stock_supplier_name_2.setFocus(True)           
        elif self.leftlist.item(3).isSelected():
            self.conf_text.setFocus(True)
          
    def tab_listener(self,val):
        if self.tabs.currentIndex() == 0: #managestockitems
                self.stock_supplier_name_1.setFocus(True)                   
        elif self.tabs.currentIndex() == 1: #managestockitems
                self.stock_name2.setFocus(True)

    def tab1_listener(self,val):
        if self.tabs1.currentIndex() == 0: #managestockcounts
                self.stock_supplier_name_2.setFocus(True)
        elif self.tabs1.currentIndex() == 1: #managestockcounts
                self.stock_name_red.setFocus(True)
        elif self.tabs1.currentIndex() == 2: #managestockcounts
                self.stock_name_del.setFocus(True)                
                
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if self.leftlist.item(0).isSelected() and self.tabs.currentIndex() == 0:
                self.on_click1()
            if self.leftlist.item(0).isSelected() and self.tabs.currentIndex() == 1:
                self.del_stock_item()
            if self.leftlist.item(1).isSelected() and self.tabs1.currentIndex() == 0:
                self.on_click2()
                
            if self.leftlist.item(1).isSelected() and self.tabs1.currentIndex() == 1:
                self.call_red()
            if self.leftlist.item(1).isSelected() and self.tabs1.currentIndex() == 2:
                self.call_del()                
            if self.leftlist.item(3).isSelected():
                self.show_search()
                #self.pop_graph(query)
                self.conf_text.setText('')
                
    def stack1UI(self):
        temp_var = False
        layout = QHBoxLayout()
        layout.setGeometry(QRect(0,300,1150,500)) # t(0,300,1150,500))
        self.tabs = QTabWidget()   
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, 'Create Stock Item')
        self.tabs.addTab(self.tab2, 'Delete Stock Item')
        self.tabfirstUI()
        self.tabsecondUI()
        layout.addWidget(self.tabs)
        self.stack1.setLayout(layout)
        #widget cizildikten sonra bunun konmasi lazim
        self.tabs.setTabEnabled(1,temp_var)
        self.tabs.currentChanged.connect(self.tab_listener)
               
    def tabfirstUI(self):
        v_layout = QVBoxLayout()
        layout = QFormLayout()
        h_layout = QHBoxLayout()
        self.lbl1 = QLabel()
        self.stock_supplier_name_1 = QLineEdit()
        self.stock_supplier_name_1.setFocusPolicy(Qt.StrongFocus)      
        layout.addRow("Supplier name", self.stock_supplier_name_1)
        self.stock_category_name = QLineEdit()
        layout.addRow("Category Name", self.stock_category_name)
        self.stock_item_code = QLineEdit()
        self.stock_item_code.setValidator(QIntValidator())
        layout.addRow("Item Code", self.stock_item_code)
        self.stock_name = QLineEdit()
        layout.addRow("Stock Name", self.stock_name)
        self.stock_uom = QLineEdit() # added later 
        layout.addRow("Unit of measurement", self.stock_uom)  
        self.stock_size = QLineEdit()
        layout.addRow("Dimensions (WxH)",self.stock_size)      
        self.stock_thickness = QLineEdit()
        layout.addRow("Thickness",self.stock_thickness)
        self.stock_min = QLineEdit()
        self.stock_min.setValidator(QIntValidator())
        layout.addRow("Minimum Stock Point",self.stock_min)   
        
        self.ok = QPushButton('Create Stock Item', self)
        cancel = QPushButton('Cancel', self)
        v_layout.setSpacing(30)
        h_layout.addWidget(self.ok)
        h_layout.addWidget(cancel)
        
         
        self.ok.clicked.connect(self.on_click1)
        cancel.clicked.connect(self.stock_supplier_name_1.clear)
        cancel.clicked.connect(self.stock_name.clear)
        cancel.clicked.connect(self.stock_category_name.clear)
        cancel.clicked.connect(self.stock_item_code.clear)
        cancel.clicked.connect(self.stock_uom.clear)
        cancel.clicked.connect(self.stock_size.clear)
        cancel.clicked.connect(self.stock_min.clear)
        cancel.clicked.connect(self.stock_thickness.clear)
        
        v_layout.addLayout(layout)
        v_layout.addLayout(h_layout)
        v_layout.addStretch()        
        v_layout.addWidget(self.lbl1)  
        self.tab1.setLayout(v_layout)
        
    def tabsecondUI(self):
        v_layout = QVBoxLayout()
        layout = QFormLayout()
        h_layout = QHBoxLayout()
        self.stock_name2 = QLineEdit()
        layout.addRow("Stock Name", self.stock_name2)
        self.lbl2 = QLabel()
        self.del1 = QPushButton('Delete Stock Item', self)
        cancel = QPushButton('Cancel', self)
        v_layout.setSpacing(30)        
        h_layout.addWidget(self.del1)
        h_layout.addWidget(cancel)
        self.del1.clicked.connect(self.del_stock_item)
        cancel.clicked.connect(self.stock_name2.clear)
        v_layout.addLayout(layout)
        v_layout.addLayout(h_layout)
        v_layout.addStretch()  
        v_layout.addWidget(self.lbl2)         
        self.tab2.setLayout(v_layout) 
        
    def check_string_empty(self,string):
        if len(string) >=1:
            return string
        else:
            return 0

    def on_click1(self):
        if self.stock_supplier_name_1.text() == 'on':
            self.tabs.setTabEnabled(1,True)
        if self.stock_supplier_name_1.text() == 'off':
            self.tabs.setTabEnabled(1,False)  
        missing_variable= False
        dic = {"self.stock_supplier_name_1.text()":"self.stock_supplier_name_1",
               "self.stock_category_name.text()":"self.stock_category_name",
               "self.stock_item_code.text()":"self.stock_item_code",
               "self.stock_name.text()":"self.stock_name",               
               "self.stock_uom.text()":"self.stock_uom",
               "self.stock_size.text()":"self.stock_size", 
               "self.stock_thickness.text()":"self.stock_thickness",
               "self.stock_min.text()":"self.stock_min"}
        for i in range(0,len(dic)):
            if not eval(list(dic)[i]):
                value = list(dic.values())[i]
                eval(value).setPlaceholderText("You must provide a value")
                missing_variable = True
        if missing_variable == True:
            QtWidgets.QMessageBox.warning(self, 'Error', "You must provide values for the empty lines")
        else:
            now = datetime.datetime.now()
            stock_supplier_name_inp = self.stock_supplier_name_1.text()
            stock_category_name_inp = self.stock_category_name.text().lower()
            stock_item_code_inp = self.check_string_empty(self.stock_item_code.text())
            stock_name_inp = self.stock_name.text().lower()
            print(stock_name_inp)
            stock_name_inp = " ".join(stock_name_inp.split())
            print(stock_name_inp)
            stock_uom_inp = self.stock_uom.text().lower()
            stock_size_inp = self.stock_size.text().lower()
            stock_thickness_inp = self.stock_thickness.text().lower()
            stock_add_date_time = now.strftime("%Y-%m-%d %H:%M")
            stock_min_inp = self.check_string_empty(self.stock_min.text())
            check = mp.insert_prod(stock_supplier_name_inp,stock_category_name_inp,stock_item_code_inp,stock_name_inp\
                          ,stock_uom_inp,stock_size_inp,stock_thickness_inp,stock_add_date_time,stock_min_inp)
            if check is not None:
                QtWidgets.QMessageBox.warning(self, 'Error', "Either the stock name:'%s' or item code:'%s' already defines a stock item record in the database. Choose different stock name and item code combination" % (stock_name_inp,stock_item_code_inp))
            else:
                self.lbl1.setText('Created a new stock item')
                self.timer.start(2500)
                
    def del_stock_item(self):
        missing_variable= False
        dic = {"self.stock_name2.text()":"self.stock_name2"}
        for i in range(0,len(dic)):
            if not eval(list(dic)[i]):
                value = list(dic.values())[i]
                eval(value).setPlaceholderText("You must provide a value")
                missing_variable = True
        if missing_variable == True:
            QtWidgets.QMessageBox.warning(self, 'Error', "You must provide values for the empty lines")
        else:    
            stock_name_inp = self.stock_name2.text()
            check = mp.del_stock(stock_name_inp)
            if check is None:
                QtWidgets.QMessageBox.warning(self, 'Error', "Item with the provided name:'%s' is not found in the database" % (stock_name_inp))
            else:
                self.lbl2.setText('Deleted a stock item')
                self.timer.start(2500)
        
    def stack2UI(self):
        temp_var = False
        layout = QHBoxLayout()
        layout.setGeometry(QRect(0,300,1150,500))
        self.tabs1 = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()     
        self.tabs1.addTab(self.tab1, 'Create Stock Entry')
        self.tabs1.addTab(self.tab2, 'Reduce Stock Entry')
        self.tabs1.addTab(self.tab3, 'Delete Stock Entry')
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        layout.addWidget(self.tabs1)
        self.stack2.setLayout(layout)
        self.tabs1.setTabEnabled(2,temp_var) # make delete stock entry tab passive to prevent unwanted deletion
        self.tabs1.currentChanged.connect(self.tab1_listener)
        
    def tab1UI(self):
        v_layout = QVBoxLayout()
        layout = QFormLayout()
        h_layout = QHBoxLayout()
        self.lbl4 = QLabel()
        self.stock_supplier_name_2 = QLineEdit()
        layout.addRow("Supplier name", self.stock_supplier_name_2)
        self.stock_name1 = QLineEdit()
        layout.addRow("Stock Name", self.stock_name1)
        self.stock_count1 = QLineEdit()
        self.stock_count1.setValidator(QIntValidator())
        layout.addRow("Quantity", self.stock_count1)
        self.stock_cost1 = QLineEdit()
        layout.addRow("Cost of Stock (per uom)", self.stock_cost1)
        self.supp_item_name = QLineEdit()
        layout.addRow("Supplier Item Name",self.supp_item_name)    
        self.cost1 = QPushButton('Create Stock Entry', self)
        cancel = QPushButton('Cancel', self)
        v_layout.setSpacing(30)        
        h_layout.addWidget(self.cost1)
        h_layout.addWidget(cancel)
        self.cost1.clicked.connect(self.on_click2)
        cancel.clicked.connect(self.stock_supplier_name_2.clear)
        cancel.clicked.connect(self.stock_name1.clear)
        cancel.clicked.connect(self.stock_cost1.clear)
        cancel.clicked.connect(self.stock_count1.clear)
        cancel.clicked.connect(self.supp_item_name.clear) 
        v_layout.addLayout(layout)
        v_layout.addLayout(h_layout)
        v_layout.addStretch()
        v_layout.addWidget(self.lbl4)
        self.tab1.setLayout(v_layout) 

    def tab2UI(self):
        v_layout = QVBoxLayout()
        layout = QFormLayout()
        h_layout = QHBoxLayout()    
        self.lbl5 = QLabel()
        self.stock_name_red = QLineEdit()
        layout.addRow("Stock Name", self.stock_name_red)
        self.stock_count_red = QLineEdit()
        self.stock_count_red.setValidator(QIntValidator())
        layout.addRow("Quantity to reduce", self.stock_count_red)        
        self.ok_red = QPushButton('Reduce Stock Entry', self)
        cancel = QPushButton('Cancel', self)
        v_layout.setSpacing(30)        
        h_layout.addWidget(self.ok_red)
        h_layout.addWidget(cancel)
        self.ok_red.clicked.connect(self.call_red) 
        cancel.clicked.connect(self.stock_name_red.clear)
        cancel.clicked.connect(self.stock_count_red.clear)    
        v_layout.addLayout(layout)
        v_layout.addLayout(h_layout)
        v_layout.addStretch()
        v_layout.addWidget(self.lbl5)
        self.tab2.setLayout(v_layout) 

    def tab3UI(self):
        v_layout = QVBoxLayout()
        layout = QFormLayout()
        h_layout = QHBoxLayout()
        self.lbl6 = QLabel()        
        self.stock_name_del = QLineEdit()
        layout.addRow("Stock Name", self.stock_name_del)        
        self.ok_del = QPushButton('Delete Stock Entry', self)
        cancel = QPushButton('Cancel', self)
        v_layout.setSpacing(30)        
        h_layout.addWidget(self.ok_del)
        h_layout.addWidget(cancel)
        self.ok_del.clicked.connect(self.call_del) 
        cancel.clicked.connect(self.stock_name_del.clear)
        v_layout.addLayout(layout)
        v_layout.addLayout(h_layout)
        #v_layout.addStretch()
        v_layout.addWidget(self.lbl6)
        self.tab3.setLayout(v_layout)
        
    def empty_label(self):
        self.lbl1.setText('')
        self.lbl2.setText('')
        self.lbl4.setText('')
        self.lbl5.setText('')
        self.lbl6.setText('')        
        #self.timer.stop()       
        
    def on_click2(self):
        missing_variable= False
        dic = {"self.stock_supplier_name_2.text()":"self.stock_supplier_name_2",
               "self.stock_name1.text()":"self.stock_name1",               
               "self.stock_count1.text()":"self.stock_count1",
               "self.stock_cost1.text()":"self.stock_cost1",
               "self.supp_item_name.text()":"self.supp_item_name"}               
        for i in range(0,len(dic)):
            if not eval(list(dic)[i]):
                value = list(dic.values())[i]
                eval(value).setPlaceholderText("You must provide a value")
                missing_variable = True
        if missing_variable == True:
            QtWidgets.QMessageBox.warning(self, 'Error', "You must provide values for the empty lines")
        else:
            now = datetime.datetime.now()
            stock_supplier_name_inp = self.stock_supplier_name_2.text()
            stock_name_inp = self.stock_name1.text().lower()
            stock_name_inp = " ".join(stock_name_inp.split())
            stock_count_inp = self.check_string_empty(self.stock_count1.text())
            stock_cost_inp = self.check_string_empty(self.stock_cost1.text())
            stock_add_date_time = now.strftime("%Y-%m-%d %H:%M")
            supp_item_name_inp = self.supp_item_name.text().lower()            
            check = mp.insert_cost(stock_supplier_name_inp,stock_name_inp,stock_count_inp,stock_cost_inp,stock_add_date_time,supp_item_name_inp)
            if check is None:
                QtWidgets.QMessageBox.warning(self, 'Error', "A stock item with the name:'%s' does not exist in the database. Provide a correct stock name" % (stock_name_inp))
            else:
                self.lbl4.setText('Created a new stock entry')
                self.timer.start(2500)


    def call_red(self):
        if self.stock_name_red.text() == 'on':
            self.tabs1.setTabEnabled(2,True)
        if self.stock_name_red.text() == 'off':
            self.tabs1.setTabEnabled(2,False)            
        missing_variable= False
        dic = {"self.stock_name_red.text()":"self.stock_name_red",
               "self.stock_count_red.text()":"self.stock_count_red"}
        for i in range(0,len(dic)):
            if not eval(list(dic)[i]):
                value = list(dic.values())[i]
                eval(value).setPlaceholderText("You must provide a value")
                missing_variable = True
        if missing_variable == True:
            QtWidgets.QMessageBox.warning(self, 'Error', "You must provide values for the empty lines")
        else:    
            now = datetime.datetime.now()
            stock_red_date_time = now.strftime("%Y-%m-%d %H:%M")
            stock_name = self.stock_name_red.text()
            stock_val = -(int(self.stock_count_red.text()))
            check = mp.update_quantity(stock_name, stock_val)
            if check is None:
                QtWidgets.QMessageBox.warning(self, 'Error', "A stock item with the name:'%s' does not exist in the database. Provide a correct stock name" % (stock_name))
            else:
                self.lbl5.setText('Reduced a stock entry')   
                self.timer.start(1000)
                
    def call_del(self): 
        missing_variable= False   
        dic = {"self.stock_name_del.text()":"self.stock_name_del",
               "self.stock_name_del.text()":"self.stock_name_del"}
        for i in range(0,len(dic)):
            if not eval(list(dic)[i]):
                value = list(dic.values())[i]
                eval(value).setPlaceholderText("You must provide a value")
                missing_variable = True
        if missing_variable == True:
            QtWidgets.QMessageBox.warning(self, 'Error', "You must provide values for the empty lines")
        else:    
            now = datetime.datetime.now()
            stock_del_date_time = now.strftime("%Y-%m-%d %H:%M")
            stock_name = self.stock_name_del.text()
            check = mp.remove_stock(stock_name)
            if check is None:
                QtWidgets.QMessageBox.warning(self, 'Error', "A stock item with the name:'%s' does not exist in the database. Provide a correct stock name" % (stock_name))
            else:
                self.lbl6.setText('Deleted stock entries')
                self.timer.start(2500)

        
    def stack3UI(self):
        #table = mp.show_stock()
        layout = QVBoxLayout()
        self.srb = QPushButton()
        self.srb.setText("Get Search Result.")
        self.View = QTableWidget()
        self.View.setSortingEnabled(1)
        self.lbl3 = QLabel()
        self.lbl_conf_text = QLabel()
        self.lbl_conf_text.setText("Enter the search keyword:")
        self.conf_text = QLineEdit(self)

        
        #self.View.setItem(0, 1, QTableWidgetItem('Category Name'))
        #self.View.setItem(0, 2, QTableWidgetItem('Item Code'))
        #self.View.setItem(0, 3, QTableWidgetItem('Stock Name'))
        #self.View.setItem(0, 4, QTableWidgetItem('Total Cost'))
        #self.View.setItem(0, 5, QTableWidgetItem('Total Quantity'))
        #self.View.setItem(0, 6, QTableWidgetItem('Size'))
        #self.View.setItem(0, 7, QTableWidgetItem('Thickness'))
        #self.View.setItem(0, 8, QTableWidgetItem('Date'))
  
        layout.addWidget(self.View)
        layout.addWidget(self.lbl_conf_text)
        layout.addWidget(self.conf_text)
        layout.addWidget(self.srb)
        layout.addWidget(self.lbl3)
        self.srb.clicked.connect(self.show_search)
        self.stack3.setLayout(layout)
        gc.collect()
    
    def search_keywords(self,string):
        if string == '':
            query_string = ''
            search_m = ''
            func_index_ls = []
            func_ls = []
        else:
            func_index_ls=[]
            func_keywords_in_string =[]
            func_ls=["min","max"]
            keyword_ls=string.split()
            for keyword in keyword_ls:
                if keyword in func_ls:
                    try:
                        func_index_ls.append(func_ls.index(keyword))
                        func_keywords_in_string.append(keyword)                        
                    except ValueError as e:
                        pass

            func_keywords_removed = list(OrderedSet(keyword_ls)-set(func_keywords_in_string))
            query_string = ' '.join(func_keywords_removed)
            #declare keyword and search mode 
            if query_string.startswith(".") == True and query_string.startswith("..") == False:
                search_m = "cat"
                query_string = query_string[1:]
            elif query_string.startswith("..") == True:
                search_m = "supp"
                query_string = query_string[2:]
            else:
                search_m = ''
        print(query_string,func_ls,func_index_ls,search_m)
        return string,query_string,search_m,func_index_ls,func_ls
       
    def query_with_search_mode(self,search_m,query_string,func_keyword=None):
        if not search_m: #if string does not have search mode
            print("if")
            query_result = mp.show_stock(query_string,func_keyword)
        elif search_m == "cat": #if search mode is category
            print("elif1")
            query_result = mp.show_cat(query_string,func_keyword)
        elif search_m == "supp": #if search mode is supplier
            print("elif2")
            query_result = mp.show_supp(query_string,func_keyword)
        return query_result
        
        
    def query_with_func(self,string,query_string,search_m,func_index_ls,func_ls):
        query_string = query_string.lower()
        if not string: #if string is empty
            query_result = mp.show_stock()     
        elif not func_index_ls: #if string does not have func keywords
                query_result = self.query_with_search_mode(search_m,query_string)
        elif func_index_ls: #if string has func keywords
            for i in func_index_ls:
                func_keyword = func_ls[i]
                print(func_keyword)
                query_result = self.query_with_search_mode(search_m,query_string,func_keyword)
                print(query_result)
        return query_result
       
                          
    def show_search(self):
        self.View.setSortingEnabled(0) # so that the rows dont get messed up
        if self.View.rowCount()>0:
            for i in range(1,self.View.rowCount()):
                self.View.removeRow(0)
        
        string,query_string,search_m,func_index_ls,func_ls = self.search_keywords(self.conf_text.text())
        query_result = self.query_with_func(string,query_string,search_m,func_index_ls,func_ls)
            
        if len(query_result)!=0:
            for i in range(1,len(query_result)+1):
                self.View.insertRow(i)
                a = list(query_result[i-1])
                self.View.setItem(i, 0, QTableWidgetItem(a[0].replace('_',' ')))
                self.View.setItem(i, 1, QTableWidgetItem(str(a[1])))
                self.View.setItem(i, 2, QTableWidgetItem(str(a[2])))
                self.View.setItem(i, 3, QTableWidgetItem(str(a[3])))
                self.View.setItem(i, 4, QTableWidgetItem(f"{a[4]:,.2f}" + " €"))
                count = QTableWidgetItem()
                count.setData(Qt.DisplayRole,(a[5]))
                self.View.setItem(i, 5, count)
                self.View.setItem(i, 6, QTableWidgetItem(str(a[6])))
                self.View.setItem(i, 7, QTableWidgetItem(str(a[7])))
                self.View.setItem(i, 8, QTableWidgetItem(str(a[8])))
                self.View.setItem(i, 9, QTableWidgetItem(str(a[9])))
                self.View.setRowHeight(i, 50)
            self.lbl3.setText('Viewing Stock Database.')
            self.View.removeRow(0)          
        else:
            self.View.removeRow(0)
            self.lbl3.setText('No valid information in database.')
            self.View.insertRow(0)
            query_result = []
        self.View.setSortingEnabled(1)# so that the rows dont get messed up
        self.stack4UI(query_result)
        #del a , string , query_string, search_m, func_index_ls, func_ls, count
        #gc.collect()
        return query_result

    def stack4UI(self, query):
        self.plot.clear()       
        if query is None:
            query = self.show_search()
        self.Stack.removeWidget(self.stack4)
        self.stack4 = QWidget()
        layout = QVBoxLayout()
        data = np.empty((0, 2), int)
        for i in range(0,len(query)):
            data = np.append(data, np.array([[query[i][3],query[i][5]]]), axis=0)
        x_list = list(map(int, data[:,1]))
        y_list = [[i] for i in list(data[:,0])]
        data = [x+[y] for x, y in zip(y_list, x_list)]
        data = sorted(data, key=lambda x: x[1], reverse=False)
        x =[item[1] for item in data]
        y =[item[0] for item in data]
        bargraph = pg.BarGraphItem(x0=0, y=range(len(x)), width=x, height=0.4)
        
        stringaxis = pg.AxisItem(orientation='left')
        ydict=dict(enumerate(y))
        stringaxis.setTicks([ydict.items()])
        self.plot.setAxisItems(axisItems = {'left': stringaxis})
        
        ay = self.plot.getAxis('bottom')
        ticks = [50,100,150,200,250,300,450]
        ay.setTicks([[(v, str(v)) for v in ticks ]])
        
        self.plot.addItem(bargraph)
        self.plot.enableAutoRange(enable= True)
        layout.addWidget(self.plot)
        
        if self.stack4.layout() == None:
            self.stack4.setLayout(layout)
        self.Stack.addWidget(self.stack4)
        gc.collect()  
          
            
    def display(self, i):
        self.Stack.setCurrentIndex(i)



    def stack5UI(self):
        layout = QHBoxLayout()
        sublay1 = QVBoxLayout()
        sublay2 = QVBoxLayout()
        sublay3 = QVBoxLayout()
        sublay4 = QVBoxLayout()
        sublay5 = QVBoxLayout()
        sublay6 = QVBoxLayout()
        
        self.ch1_lbl = QLabel()
        self.ch1_lbl.setText("WOOD AREA")
        self.ch2_lbl = QLabel()
        self.ch2_lbl.setText("FABRIC AREA")
        self.ch3_lbl = QLabel()
        self.ch3_lbl.setText("PACKING AREA")
        
        self.ch4_lbl = QLabel()
        self.ch4_lbl.setText("ANOTHER AREA")
        self.ch5_lbl = QLabel()
        self.ch5_lbl.setText("ANOTHER AREA")
        self.ch6_lbl = QLabel()
        self.ch6_lbl.setText("ANOTHER AREA")
        
        self.chat1 = QTextEdit()
        self.chat2 = QTextEdit()
        self.chat3 = QTextEdit()
        self.chat4 = QTextEdit()
        self.chat5 = QTextEdit()
        self.chat6 = QTextEdit()
        
        self.chat1.setReadOnly(True)
        self.chat2.setReadOnly(True)
        self.chat3.setReadOnly(True)
        self.chat4.setReadOnly(True)
        self.chat5.setReadOnly(True)
        self.chat6.setReadOnly(True)
        
        sublay1.addWidget(self.ch1_lbl)
        sublay1.addWidget(self.chat1)
        
        sublay2.addWidget(self.ch2_lbl)
        sublay2.addWidget(self.chat2)
        
        sublay3.addWidget(self.ch3_lbl)
        sublay3.addWidget(self.chat3)        

        sublay4.addWidget(self.ch4_lbl)
        sublay4.addWidget(self.chat4)
        
        sublay5.addWidget(self.ch5_lbl)
        sublay5.addWidget(self.chat5)
        
        sublay6.addWidget(self.ch6_lbl)
        sublay6.addWidget(self.chat6)  
        
        
        layout.addLayout(sublay1)
        layout.addLayout(sublay2)
        layout.addLayout(sublay3)
        layout.addLayout(sublay4)
        layout.addLayout(sublay5)
        layout.addLayout(sublay6)
        self.stack5.setLayout(layout)        
          
def main():
    app = QtWidgets.QApplication (sys.argv)
    styles.dark(app)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    login = Login()
    #
    if login.exec() == QtWidgets.QDialog.Accepted:
        window = Example()
        window.st.stock_supplier_name_1.setFocus(True)
        server_thread=TCP_server_thread(window)
        server_thread.start()
        app.exec()

if __name__ == '__main__':
    main()



