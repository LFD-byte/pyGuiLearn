import os

import PySide2
from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide2.QtUiTools import QUiLoader

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


class MediRecordTagger:
    def __init__(self):
        self.data = []  # 原始数据
        self.dataTag = []  # 标记过的数据
        self.displayData = []  # 展示在显示框里的文本
        self.sum = 0  # 原始数据总数
        self.num = 0  # 标记的对话序号
        self.utter_all = 0  # 每个对话中的话语总数
        self.utter_num = 0  # 每个对话中被比较的话语序号
        
        # 加载UI
        self.ui = QUiLoader().load('taggerUi.ui')
        # 打开文件
        self.ui.button_openFile.clicked.connect(self.openFileDialog)
        # 保存标记文件
        self.ui.button_save.clicked.connect(self.saveFileTagger)
        # 按钮跳转到下一个病历对话
        self.ui.button_nextLine.clicked.connect(self.dealNextLine)
        # 按钮跳转到上一个病历对话
        self.ui.button_lastLine.clicked.connect(self.dealLastLine)
        # 上一句、下一句
        self.ui.last_utter.clicked.connect(self.lastUtter)
        self.ui.next_utter.clicked.connect(self.nextUtter)
        # 主诉、现病史、既往史、体检、辅助检查结果、初步诊断、治疗意见、其它
        self.ui.chief_complain.clicked.connect(self.chiefComplainTag)
        self.ui.now_history.clicked.connect(self.nowHistoryTag)
        self.ui.past_history.clicked.connect(self.pastHistoryTag)
        self.ui.physical_exam.clicked.connect(self.physicalExam)
        self.ui.aux_inspect_rst.clicked.connect(self.auxInspectRstTag)
        self.ui.preli_diag.clicked.connect(self.preliDiagTag)
        self.ui.treat_opinion.clicked.connect(self.treatOpinionTag)
        self.ui.other.clicked.connect(self.otherTag)
        # 提示框
        self.qmessagebox = QMessageBox()

    '''
    读取文件
    filepath:文件路径
    '''

    def open_file(self, filepath):
        with open(filepath, 'r', encoding="utf8") as f:
            data = f.readlines()
        self.sum = len(data)
        return data

    '''
    以角色返回对话
    content:对话内容
    '''

    def getPatientAndDoctorUtter(self, content):
        PAD = []
        for utter in content:
            if utter["speaker"] == "患者":
                # PAD = PAD + "P:" + utter["utterance"] + " \n"
                PAD.append("P:" + utter["utterance"])
            else:
                # PAD = PAD + "D:" + utter["utterance"] + " \n"
                PAD.append("D:" + utter["utterance"])

        return PAD

    '''
    按钮打开文件
    '''

    def openFileDialog(self):
        # 生成文件对话框对象
        dialog = QFileDialog()
        # 设置文件过滤器，这里是任何文件，包括目录
        dialog.setFileMode(QFileDialog.AnyFile)
        # 设置显示文件的模式，这里是详细模式
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()  # 文件名
            filepath = fileNames[0]
            self.data = self.open_file(filepath)
            self.dataTag = [[] for i in range(len(self.data))]
            self.displayData = self.getPatientAndDoctorUtter(eval(self.data[0])["content"])
            self.utter_all = len(self.displayData)
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.ui.text_utter_one.setText(self.displayData[self.utter_num])
            self.ui.text_numOfAll.setText(str(self.num + 1) + '/' + str(self.sum))
            self.num += 1

    # 保存标记文件
    def saveFileTagger(self):
        path = self.ui.lineEdit.text()
        # 文件是否已存在
        if os.path.isfile(path):
            self.qmessagebox.warning(self.ui, "警告", "文件已存在")
        # 创建新文件
        else:
            pathList = []
            if '\\' in path:
                pathList = path.split('\\')
            elif '/' in path:
                pathList = path.split('/')
            if os.path.isdir('/'.join(pathList[:-1])):
                with open(path, 'w', encoding="utf8") as f:
                    for i in range(self.sum):
                        if self.dataTag[i] != []:
                            # print(self.dataTag[i])
                            f.write('\n'.join(self.dataTag[i]))
                            # print(self.dataTag[i])
                        else:
                            f.write('\n')

    def dataAddTag(self):
        self.num -= 1
        data_dict = eval(self.data[self.num])
        rcdId = "id" + ' ' + data_dict["id"]
        apartment = "apartment" + ' '
        disease = "disease" + ' '
        metaInfo = rcdId + apartment + disease
        SumAB = "SUM1 " + data_dict["summary"]["description"] + '\n' + "SUM2.0 " + data_dict["summary"]["suggestion"]

        self.dataTag[self.num] = [metaInfo, '\n'.join(self.displayData), SumAB + '\n']
        # print(self.num)
        self.num += 1

    # 跳转到下一条病历
    def dealNextLine(self):
        if self.num < self.sum:
            self.dataAddTag()
            self.displayData = self.getPatientAndDoctorUtter(eval(self.data[self.num])["content"])
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.ui.text_numOfAll.setText(str(self.num + 1) + '/' + str(self.sum))
            self.utter_num = 0
            self.utter_all = len(self.displayData)
            self.num += 1
        else:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")

    # 跳转到上一条病历
    def dealLastLine(self):
        if self.num > 1:
            self.num -= 2
            self.displayData = self.getPatientAndDoctorUtter(eval(self.data[self.num])["content"])
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.ui.text_numOfAll.setText(str(self.num + 1) + '/' + str(self.sum))
            self.num += 1
        else:
            self.qmessagebox.information(self.ui, "提示", "已到达首句")

    # 上一句、下一句
    def lastUtter(self):
        if self.utter_num > 0:
            self.utter_num -= 1
        else:
            self.utter_num = 0
        self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    def nextUtter(self):
        if self.utter_num < self.utter_all - 1:
            self.utter_num += 1
        else:
            self.utter_num = self.utter_all - 1
        self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 标记为主诉
    def chiefComplainTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 0'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 现病史
    def nowHistoryTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 1'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 既往史
    def pastHistoryTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 2'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 体格检查
    def physicalExam(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 3'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 辅助检查结果
    def auxInspectRstTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 4'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 初步诊断
    def preliDiagTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")

        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 5'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 治疗意见
    def treatOpinionTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 6'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])

    # 其他
    def otherTag(self):
        if self.utter_num >= self.utter_all:
            self.qmessagebox.information(self.ui, "提示", "已到达最后一句")
        else:
            self.displayData[self.utter_num] = self.displayData[self.utter_num] + ' 7'
            self.ui.text_utter.setText('\n'.join(self.displayData))
            self.utter_num += 1
            if self.utter_num < self.utter_all:
                self.ui.text_utter_one.setText(self.displayData[self.utter_num])


app = QApplication([])
tagger = MediRecordTagger()
tagger.ui.show()
app.exec_()
