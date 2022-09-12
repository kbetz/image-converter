import sys, os
import numpy as np
import cv2 as cv
from tqdm import tqdm

from PyQt5 import QtCore, QtGui, QtWidgets

# COMPILE WITH: python -O -m PyInstaller --noconsole --onefile/onedir test.spec

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setFixedSize(400, 500)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.group_info = QtWidgets.QGroupBox(self.centralwidget)
        self.group_info.setGeometry(QtCore.QRect(10, 10, 381, 101))
        self.group_info.setObjectName("group_info")
        self.label_info = QtWidgets.QLabel(self.group_info)
        self.label_info.setGeometry(QtCore.QRect(20, 20, 331, 71))
        self.label_info.setObjectName("label_info")
        self.group_action = QtWidgets.QGroupBox(self.centralwidget)
        self.group_action.setGeometry(QtCore.QRect(10, 120, 381, 141))
        self.group_action.setObjectName("group_action")
        
        self.btn_res = QtWidgets.QPushButton(self.group_action)
        self.btn_res.setGeometry(QtCore.QRect(90, 60, 281, 23))
        self.btn_res.setObjectName("btn_target")
        self.btn_res.clicked.connect(lambda: self.choose_path(False))
        self.btn_img = QtWidgets.QPushButton(self.group_action)
        self.btn_img.setGeometry(QtCore.QRect(90, 20, 281, 23))
        self.btn_img.setObjectName("btn_img")
        self.btn_img.clicked.connect(lambda: self.choose_path(True))
        
        self.lbl_img = QtWidgets.QLabel(self.group_action)
        self.lbl_img.setGeometry(QtCore.QRect(20, 20, 61, 22))
        self.lbl_img.setObjectName("lbl_img")
        self.lbl_res = QtWidgets.QLabel(self.group_action)
        self.lbl_res.setGeometry(QtCore.QRect(20, 60, 61, 22))
        self.lbl_res.setObjectName("lbl_target")
        
        self.btn_convert = QtWidgets.QPushButton(self.group_action)
        self.btn_convert.setGeometry(QtCore.QRect(10, 100, 231, 31))
        self.btn_convert.setObjectName("btn_convert")
        self.btn_convert.clicked.connect(self.convert)
        self.btn_stop = QtWidgets.QPushButton(self.group_action)
        self.btn_stop.setGeometry(QtCore.QRect(260, 100, 111, 31))
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self.abort)
        
        self.group_status = QtWidgets.QGroupBox(self.centralwidget)
        self.group_status.setGeometry(QtCore.QRect(10, 270, 381, 201))
        self.group_status.setObjectName("group_status")
        self.progress_bar = QtWidgets.QProgressBar(self.group_status)
        self.progress_bar.setGeometry(QtCore.QRect(10, 20, 361, 20))
        #self.progress_bar.setProperty("value", 24)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        
        self.text_edit = QtWidgets.QTextEdit(self.group_status)
        self.text_edit.setGeometry(QtCore.QRect(10, 60, 361, 131))
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setReadOnly(True)
        
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 400, 21))
        self.menubar.setObjectName("menubar")
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setObjectName("menu_help")
        self.setMenuBar(self.menubar)
        self.menubar.addAction(self.menu_help.menuAction())
        
        self.action_about = QtWidgets.QAction(self)
        self.action_about.setObjectName("action_about")
        self.action_about.triggered.connect(self.about)
        self.menu_help.addAction(self.action_about)
        
        self.action_settings = QtWidgets.QAction(self)
        self.action_settings.setObjectName("action_settings")
        self.action_settings.triggered.connect(self.settings)
        self.menu_help.addAction(self.action_settings)
        
        self.file_diag_img = QtWidgets.QFileDialog(self)
        self.file_diag_img.accepted.connect(lambda: self.set_path(True))
        self.file_diag_img.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        self.file_diag_img.setFileMode(QtWidgets.QFileDialog.Directory)
        self.file_diag_res = QtWidgets.QFileDialog(self)
        self.file_diag_res.accepted.connect(lambda: self.set_path(False))
        self.file_diag_res.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        self.file_diag_res.setFileMode(QtWidgets.QFileDialog.Directory)
        
        # VALUES
        self.curr_dir = str(os.path.expanduser(""))
        self.thread = None
        self.stop = False
        self.square_size = 1200
        
    def retranslate(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "aBbuZ"))
        self.group_info.setTitle(_translate("MainWindow", "Info"))
        self.label_info.setText(_translate("MainWindow", "Zum Starten einen Pfad zu den Bildern und einen Zielordner\n"
"für die JPG-Dateien auswählen.\n\n"
"Dann \"Konvertieren\" drücken oder Ordnerauswahl korrigieren,\n"
"falls die Pfade nicht gefunden wurden (siehe Statusanzeige)."))
        self.group_action.setTitle(_translate("MainWindow", "Aktionen"))
        self.btn_res.setText(_translate("MainWindow", "Wählen..."))
        self.btn_img.setText(_translate("MainWindow", "Wählen..."))
        self.lbl_img.setText(_translate("MainWindow", "Bildordner:"))
        self.lbl_res.setText(_translate("MainWindow", "Zielordner:"))
        self.btn_convert.setText(_translate("MainWindow", "Konvertieren"))
        self.btn_stop.setText(_translate("MainWindow", "Abbrechen"))
        self.group_status.setTitle(_translate("MainWindow", "Status"))
        self.text_edit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">...</p></body></html>"))
        self.text_edit.setText("[aBbuZ v1.0]")
        self.menu_help.setTitle(_translate("MainWindow", "Hilfe"))
        self.action_about.setText(_translate("MainWindow", "Über"))
        self.action_settings.setText(_translate("MainWindow", "Optionen"))
        
    @QtCore.pyqtSlot()
    def about(self):
        diag = QtWidgets.QMessageBox(self)
        diag.setWindowTitle("Über")
        diag.setText("Mit diesem Programm werden alle Bilder in einem Ordner zu JPGs\n"
"der Größe 1200x1200 kovertieret.\n"
"Die Größe des Quadrats lässt sich in den Zusatzoptionen (Hilfe -> Optionen) ändern.\n"
"Im Statusbereich befindet sich eine Fortschrittsleiste, sowie eine Konsole, die den aktuellen Status ausgibt.\n")
        diag.open()  
        
    @QtCore.pyqtSlot()
    def settings(self):
            
        diag = QtWidgets.QDialog(self, QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        #diag.setWindowFlags()
        diag.setWindowTitle("Optionen")
        spinbox = QtWidgets.QSpinBox(diag)
        
        @QtCore.pyqtSlot()
        def dummy():
            self.square_size = spinbox.value()
            
        spinbox.setGeometry(QtCore.QRect(10, 10, 111, 31))
        spinbox.setMinimum(100)
        spinbox.setMaximum(4000)
        spinbox.setValue(self.square_size)
        spinbox.valueChanged.connect(dummy)
        diag.open()
        
    @QtCore.pyqtSlot(bool)
    def choose_path(self, mode):
        if mode:
            self.file_diag_img.setDirectory(str(self.curr_dir))
            self.file_diag_img.open()
        else:
            self.file_diag_res.setDirectory(str(self.curr_dir))
            self.file_diag_res.open()
        
    @QtCore.pyqtSlot(bool)
    def set_path(self, mode):
        if mode:
            text = self.file_diag_img.selectedFiles()[0]
            self.btn_img.setText(text)
            self.curr_dir = os.path.dirname(text)
        else:
            text = self.file_diag_res.selectedFiles()[0]
            self.btn_res.setText(text)
            self.curr_dir = os.path.dirname(text)
            
    @QtCore.pyqtSlot()
    def convert(self):
    
        self.stop = False
        path_in = self.btn_img.text()
        path_out = self.btn_res.text()
        test1, test2 = False, False
        
        if not os.path.isdir(path_in):
            #print("Invalid input path! Terminating...")
            self.message("Ungültiger Bildordner!")
            test1 = True
            
        if not os.path.isdir(path_out):
            #print("Invalid output path! Terminating...")
            self.message("Ungültiger Zielordner!")
            test2 = True
            
        if test1 or test2:
            return
            
        if self.thread:
            if not self.thread.isFinished():
                return
                
        self.update_progress(0)
        self.message("Vorgang wird ausgeführt")
        
        self.thread = Worker(path_in, path_out, self, self.square_size)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished.connect(self.finished)
        self.thread.start()
        
    @QtCore.pyqtSlot()
    def abort(self):
        if not self.thread:
            return
            
        if self.thread.isFinished():
            return
            
        self.message("Vorgang wird gestoppt")
        self.stop = True
        
    @QtCore.pyqtSlot()
    def finished(self):
        if self.progress_bar.value() == 100:
            self.message("Vorgang abgeschlossen")
        else:
            self.message("Vorgang abgebrochen")
        
    @QtCore.pyqtSlot(str)
    def message(self, msg):
        self.text_edit.append("> " + msg)
        
    @QtCore.pyqtSlot(int)
    def update_progress(self, value):
        val = min(100,value)
        self.progress_bar.setValue(val)
        self.progress_bar.update()
    
    
class Worker(QtCore.QThread):

    progress_signal = QtCore.pyqtSignal(int)
    break_signal = QtCore.pyqtSignal()
    
    def __init__(self, path_in, path_out, gui, sq):
        super().__init__()
        self.path_in = path_in
        self.path_out = path_out
        self.gui = gui
        self.square_size = sq
        
    def run(self):
        self.main(self.path_in, self.path_out)
        
    def workit(self, im):

        # Find out whether to use contour cropping
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        use_cont = True
        
        if (imgray[0,0] == imgray[0,im.shape[1]-1] == imgray[im.shape[0]-1,0] == imgray[im.shape[0]-1,im.shape[1]-1]):
            base_color = imgray[0,0]
            
            for i in range(im.shape[1]):
                if imgray[0,i] != base_color or imgray[im.shape[0]-1,i] != base_color:
                    use_cont = False
                    break
                    
            if use_cont:
                for j in range(1, im.shape[0]-1):
                    if imgray[j,0] != base_color or imgray[j,im.shape[1]-1] != base_color:
                        use_cont = False
                        break
                        
        else:
            #print(im[0,0])
            #print(im[0,im.shape[1]-1])
            #print(im[im.shape[0]-1,0])
            #print(im[im.shape[0]-1,im.shape[1]-1])
            use_cont = False
        
        if use_cont:
            
            # Compute contours
            ret, thresh = cv.threshold(imgray, 240, 255, 0)
            contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            max_val = 0
            max_ind = -1
            max_val2 = 0
            max_ind2 = -1
            
            # Find second largest contour
            for i, cont in enumerate(contours):
                area = cv.contourArea(cont)
                if area > max_val:
                    max_val = area
                    max_ind = i
                elif area < max_val and area > max_val2:
                    max_val2 = area
                    max_ind2 = i
                    
            # Get bounding box
            try:
                x, y, w, h = cv.boundingRect(contours[max_ind2])
            except:
                x, y, w, h = 0,0,im.shape[1],im.shape[0]
                
            x_min = max(0, x-4)
            y_min = max(0, y-4)
            x_max = min(im.shape[1], x+w+8)
            y_max = min(im.shape[0], y+h+8)
            
            # Crop image
            im = im[y_min:y_max, x_min:x_max]
            
        w = im.shape[1]
        h = im.shape[0]
        
        c_white = [255,255,255]
        
        # Pad image to square with white
        if w < h:
            diff = h-w
            plus1 = 0 if diff % 2 == 0 else 1
            
            pad_size = diff//2
            
            pad1 = np.full((h,pad_size,3), c_white, dtype=im.dtype)
            pad2 = np.full((h,pad_size+plus1,3), c_white, dtype=im.dtype)
            
            im = np.hstack((pad1,im,pad2))
            
        elif h < w:
            diff = w-h
            plus1 = 0 if diff % 2 == 0 else 1
            
            pad_size = diff//2
            
            pad1 = np.full((pad_size,w,3),       c_white, dtype=im.dtype)
            pad2 = np.full((pad_size+plus1,w,3), c_white, dtype=im.dtype)
            
            im = np.vstack((pad1,im,pad2))
            
        
        #if use_cont: 
        #    res = cv.drawContours(im, contours, -1, (0,255,0), 10)
        #else:
        res = cv.resize(im, (self.square_size,self.square_size), cv.INTER_LANCZOS4)
            
        #res = cv.resize(im, (1200,1200), cv.INTER_NEAREST)
        #res = cv.resize(im, (1200,1200), cv.INTER_LINEAR)
        #res = cv.resize(im, (1200,1200), cv.INTER_LINEAR_EXACT)
        #res = cv.resize(im, (1200,1200), cv.INTER_BITS2)
        
        #cv.imshow("image", res)
        #cv.waitKey()
        
        return res
        
        
    def main(self, path_in, path_out):

        """
        test1, test2 = False, False
        if not os.path.isdir(path_in):
            #print("Invalid input path! Terminating...")
            self.message("Ungültiger Bildordner!")
            test1 = True
            
        if not os.path.isdir(path_out):
            #print("Invalid output path! Terminating...")
            self.message("Ungültiger Zielordner!")
            test2 = True
            
        if test1 or test2:
            return 
        self.message("Vorgang wird ausgeführt...")
        """  
        
        byte_limit = 210*1024
        comp_qualy = 100
        
        curr_dir = os.listdir(path_in)
        num_files = len(curr_dir)
        
        #self.stop = False
        #for i in tqdm(range(num_files)):
        for i in range(num_files):
            
            if self.gui.stop:
                self.progress_signal.emit(0)
                self.break_signal.emit()
                break
                
            file = curr_dir[i]
            if file.endswith(".png") \
                    or file.endswith(".jpeg") \
                    or file.endswith(".jpg"):
                    
                im = cv.imread(os.path.join(path_in, file))
                
                if im.shape[2] > 3:
                    im[im[:,:,3] == 0] = [255,255,255,255]
                    im = cv.cvtColor(im, cv.COLOR_RGBA2RGB)
                #else:
                #    im[im[:,:,:] == [0,0,0]] = 255
                    
                im_cpy = np.copy(im)
                im_cpy[:,:,0] = im[:,:,2]
                im_cpy[:,:,2] = im[:,:,0]
                
                res = self.workit(im_cpy)
                
                val, enc = cv.imencode(".jpg", res, (cv.IMWRITE_JPEG_QUALITY, comp_qualy))
                while len(enc) > byte_limit:
                    comp_qualy -= 5
                    val, enc = cv.imencode(".jpg", res, (cv.IMWRITE_JPEG_QUALITY, comp_qualy))
                
                file = os.path.splitext(file)[0]
                file += ".jpg"
                
                cv.imwrite(os.path.join(path_out, file), res, (cv.IMWRITE_JPEG_QUALITY, comp_qualy))
                #cv.imwrite(path_out+str(i)+"enc.jpg", enc)
                
                comp_qualy = 100
                i += 1
                
            progress = 100 * (1+i)/num_files
            self.progress_signal.emit(int(progress))
            #self.gui.update_progress(progress)
            #self.progress_bar.setValue()
            #self.progress_bar.update()
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    win.retranslate()
    win.show()
    sys.exit(app.exec_())
    #try:
    #    main(sys.argv[1], sys.argv[2])
    #except IndexError:
    #    print("2 path arguments required! Terminating...")
    