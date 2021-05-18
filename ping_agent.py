import subprocess
import re
import os
import time
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from threading import *
from matplotlib import pyplot as plt
from PySide2.QtGui import QIcon


class Function(object):
    def __init__(self):
        # 连接Qt界面
        qfile_stats = QFile("ui.ui")
        qfile_stats.open(QFile.ReadOnly)
        qfile_stats.close()
        self.ui = QUiLoader().load(qfile_stats)

        # 信号与槽的连接
        self.ui.ButtonRun.clicked.connect(self.main)                            # 主功能按钮连接
        self.ui.ButtonClear.clicked.connect(self.clear)                         # 清除按钮连接
        self.ui.ButtonPic.clicked.connect(self.pic)                             # 绘制折线图按钮连接
        self.ui.ButtonSavePic.clicked.connect(self.save_pic)                    # 保存图片按钮连接
        self.ui.ButtonSaveAru.clicked.connect(self.save_aru)                    # 保存数据按钮连接
        self.ui.ButtonLogin.clicked.connect(self.login)                         # 登录按钮连接
        self.ui.ButtonCreate.clicked.connect(self.create)                       # 注册按钮连接
        self.ui.ButtonStop.clicked.connect(self.stop)                           # 终止按钮连接

        # 数据初始化
        self.pic_name = 1                                                       # 初始化图片ID
        self.check_user = 0                                                     # 初始化用户登录状态指示符
        self.check_run = 1                                                      # 初始化程序运行状态指示符

    # 主功能
    # 最后修改时间 5/12 - 18点56分
    # 新增内容：
    # 1）增加指示符"check_run"控制程序的终止
    # 2）让主程序变成线程运行，提高运行速度，能够逐跳显示测试数据
    def main(self):
        self.check_run = 1
        m = self.ui.spinBox.value()                                             # 读取运行次数
        self.ui.textBrowser.clear()
        info = self.ui.lineEdit.text()                                          # 读取输入框中的内容
        def run():
            if info == '':                                                      # IP地址为空
                QMessageBox.critical(
                    self.ui,
                    '错误',
                    '请输入测试IP地址')
            elif m == 0:                                                        # 测试次数为0
                QMessageBox.critical(
                    self.ui,
                    '错误',
                    '请输入有效次数！')
            else:
                self.ui.textBrowser.append(f'————开始测试————')
                for i in range(0, m):
                    p = subprocess.Popen(["ping.exe", info],                    # 运行ping程序
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         shell=True)
                    out = p.stdout.read().decode('gbk')                         # 读取结果，将结果转换成可读形式
                    regex = re.compile(r'\w*%\w*')                              # 找出丢包率，这里通过‘%’匹配
                    packetLossRateList = regex.findall(out)
                    self.packetLossRate = packetLossRateList[0]
                    regex = re.compile(r'\w*ms')                                # 找出往返时间，这里通过‘ms’进行正则匹配
                    timeList = regex.findall(out)
                    self.minTime = timeList[-3]
                    self.maxTime = timeList[-2]
                    self.averageTime = timeList[-1]
                    time_now = time.asctime(time.localtime(time.time()))        # 读取测试时的时间
                    self.ui.textBrowser.append(f'''第{i+1}次测试中...              
                                               \n平均时延:{self.averageTime}
                                               \n丢包率:{self.packetLossRate}
                                               \n测试时间:{time_now}
                                               \n'''
                                               )                                # 将结果打印在文本框中
                    if self.check_run == 0:                                     # 判断测试是否终止
                        break
                if self.check_run != 0:
                    self.ui.textBrowser.append(f'————测试完毕————')
                    QMessageBox.information(
                        self.ui,
                        '操作成功',
                        '时延测试完成')
                elif self.check_run == 0:
                    QMessageBox.information(
                        self.ui,
                        '操作成功',
                        '时延测试终止')
                    self.ui.textBrowser.append(f'测试终止...')
        t1 = Thread(target=run)                                                # 采用线程方式运行程序，提高程序的可操作性
        t1.start()

    # 清除功能
    # 最后修改时间 5.6-18点21分
    def clear(self):
        choice = QMessageBox.question(
            self.ui,
            '确认',
            '确定要清空文本嘛？')
        if choice == QMessageBox.Yes:
            self.ui.textBrowser.clear()
        else:
            pass

    # 绘制折线图功能
    # 修改时间 5/12 - 18点56分
    # 新增内容：
    # 1）增加指示符"check_run"控制程序的终止
    # 修改时间 5/17 - 22点26分
    # 修改内容：
    # 1）解决matplotlib图片中文乱码问题
    def pic(self):
        self.check_run = 1
        m = self.ui.spinBox.value()
        ax = []                                        # 定义一个 x 轴的空列表用来接收动态的数据
        ay = []                                        # 定义一个 y 轴的空列表用来接收动态的数据
        plt.ion()                                      # 开启一个画图的窗口
        if m == 0:                                     # 判断测试次数是否为0
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入有效次数！')
        for i in range(0, m):                          # 遍历
            if self.check_run == 0:                    # 终止
                break
            info = self.ui.lineEdit.text()
            p = subprocess.Popen(["ping.exe", info],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            out = p.stdout.read().decode('gbk')
            regex = re.compile(r'\w*%\w*')
            packetLossRateList = regex.findall(out)
            self.packetLossRate = packetLossRateList[0]
            regex = re.compile(r'\w*ms')
            timeList = regex.findall(out)
            self.averageTime = timeList[-1]
            y = self.averageTime
            y = list(y)
            y.pop(-1)
            y.pop(-1)
            y = float(''.join(y))
            ax.append(i)                                # 添加 i 到 x 轴的数据中
            ay.append(y)
            plt.clf()                                   # 清除之前画的图
            plt.plot(ax, ay)                            # 画出当前 ax 列表和 ay 列表中的值的图形
            plt.pause(0.1)                              # 暂停一秒
            plt.ioff()                                  # 关闭画图的窗口
        plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
        plt.title("时延测试折线图")
        plt.xlabel("测试次数")
        plt.ylabel("平均时延/ms")
        plt.savefig('./test_picture.jpg')
        if self.check_run != 0:
            QMessageBox.information(
                self.ui,
                '操作成功',
                '折线图绘制完毕')
        elif self.check_run == 0:
            QMessageBox.information(
                self.ui,
                '操作成功',
                '折线图绘制终止')

    # 图片存储功能
    # 最后修改时间 5/8 - 13点22分
    # 新增内容：
    # 1）增加用户登录后的存储路径更改
    def save_pic(self):
        if self.check_user == 0:                                                # 判断用户是否是登录状态（未登录）
            if os.path.isfile(f'./Save_Pic/{self.pic_name}.jpg'):               # 确保用户所在文件夹中图片编号不重复
                self.pic_name += 1
                test.save_pic()
            plt.savefig(f'./Save_Pic/{self.pic_name}.jpg')
            QMessageBox.information(
                self.ui,
                '操作成功',
                '图片保存成功')
        else:                                                                   # 登录状态下
            info_user = self.ui.lineUser.text()
            os.mkdir(f'./{info_user}/Save_Pic')                                 # 新建一个与用户ID匹配的文件夹单独存放图片
            if os.path.isfile(f'./{info_user}/Save_Pic/{self.pic_name}.jpg'):
                self.pic_name += 1
                test.save_pic()
            plt.savefig(f'./{info_user}/Save_Pic/{self.pic_name}.jpg')
            QMessageBox.information(
                self.ui,
                '操作成功',
                '图片保存成功')

    # 数据存储功能
    # 最后修改时间 5/8 - 14点35分
    # 新增内容：
    # 1）增加用户登录后的存储路径更改
    def save_aru(self):
        text = self.ui.textBrowser.toPlainText()
        time_now = time.asctime(time.localtime(time.time()))
        if self.check_user == 0:
            file = open('./Save_Aru.txt', 'a')
            file.write(text)
            file.write('\r\n___________________________________________________\r\n')
            file.write(time_now)
            file.write('\r\n___________________________________________________\r\n')
            QMessageBox.information(
                self.ui,
                '操作成功',
                '数据保存成功')
        else:
            info_user = self.ui.lineUser.text()
            os.mkdir(f'./{info_user}')
            file = open(f'./{info_user}/Save_Aru.txt', 'a')
            file.write(text)
            file.write('\r\n___________________________________________________\r\n')
            file.write(time_now)
            file.write('\r\n___________________________________________________\r\n')
            QMessageBox.information(
                self.ui,
                '操作成功',
                '数据保存成功')

    # 登录功能
    # 修改时间 5/10 - 19点20分
    # 修改时间 5/17 - 23点19分
    # 修改内容：
    # 1）完善判定条件，当记录用户名密码的txt文件为空时触发
    # 修改时间 5/18 - 15点28分
    # 修改内容：
    # 1）解决当用户名为空时，弹窗报错两次的问题
    def login(self):
        info_user = self.ui.lineUser.text()
        info_password = self.ui.linePassWord.text()
        if info_user == '':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入用户名')
        elif info_password == '':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入密码')
        else:
            with open('./User_Password.txt', 'r') as file:
                content = file.readlines()
                cwd = os.getcwd()
                if len(content) == 0:                     # 当txt文件为空
                    QMessageBox.critical(
                        self.ui,
                        '错误',
                        '用户名或密码错误')
                else:
                    for i in range(0, len(content)):
                        regex_user = content[i].split(':')[1]
                        regex_password = content[i].split(':')[3]
                        if info_user == regex_user:
                            if info_password == regex_password:
                                self.check_user = 1
                                QMessageBox.information(
                                    self.ui,
                                    '操作成功',
                                    f'登录成功\n存储路径为:{cwd}/{regex_user}')
                            else:
                                QMessageBox.critical(
                                    self.ui,
                                    '错误',
                                    '用户名或密码错误')

    # 注册功能
    # 修改时间 5/11 - 20点09分
    # 修改时间 5/17 - 23点25分
    # 修改内容：
    # 1）新增txt文本文件为空时的判定条件
    # 修改时间 5/18 - 15点02分
    # 修改内容：
    # 1）增加判断条件，确保注册时，不能注册用户名和账号为都为空的情况
    def create(self):
        info_user = self.ui.lineUser.text()             # 读取用户名
        info_password = self.ui.linePassWord.text()     # 读取密码
        if info_user == '':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入用户名')
        elif info_password == '':
            QMessageBox.critical(
                self.ui,
                '错误',
                '请输入密码')
        else:
            with open('./User_Password.txt', 'r') as file:  # 打开用户名密码管理的txt文件
                content = file.readlines()
            if len(content) == 0:                           # 当txt文件为空时，直接创建文件，不进行匹配
                file = open('./User_Password.txt', 'a')
                file.write(f'user:{info_user}:password:{info_password}')
                QMessageBox.information(
                    self.ui,
                    '操作成功',
                    '账户创建成功')
            else:
                for i in range(0, len(content)):                # 遍历读取txt文件中的信息
                    regex_user = content[i].split(':')[1]       # 通过冒号将字符串拆开进行匹配
                    if info_user == regex_user:                 # 用户名已经存在在文件中
                        QMessageBox.critical(
                            self.ui,
                            '错误',
                            '用户名已存在')
                file = open('./User_Password.txt', 'a')         # 用户名不存在，进行用户名和密码的输入
                file.write('\n')
                file.write(f'user:{info_user}:password:{info_password}')
                QMessageBox.information(
                    self.ui,
                    '操作成功',
                    '账户创建成功')

    # 终止功能
    # 修改时间 5/17 - 19点10分
    # 修改时间 5/17 - 22点15分
    # 新增内容：
    # 1）增加确认窗口，避免误触
    def stop(self):
        choice = QMessageBox.question(
            self.ui,
            '确认',
            '确定终止测试么?')
        if choice == QMessageBox.Yes:
            self.check_run = 0              # 将运行状态指示符置0
        else:
            pass


# 程序入口
# 最后修改时间 5/17 - 21点35分
# 修改内容：
# 1）固定窗体大小
# 2）设置背景图片
# 3）设置窗体透明度
if __name__ == '__main__':
    app = QApplication([])
    test = Function()
    test.ui.show()

    test.ui.setWindowTitle('ZJUT-时延测试小程序-By朱钟乾-201706061208')         # 设置程序名
    test.ui.setWindowIcon(QIcon('./ZJUT-LOGO.ico'))                         # 设置程序图片
    test.ui.setWindowOpacity(1)                                             # 设置窗体透明度
    app.setWindowIcon(QIcon('./warning.jpg'))                               # 设置弹窗图标
    test.ui.setFixedSize(612, 230)                                          # 固定窗体大小

    test.ui.setStyleSheet('background-image:url(./background_ZJUT.jpg)')    # 设置背景图片
    test.ui.ButtonRun.setStyleSheet('background-image:url()')
    test.ui.ButtonClear.setStyleSheet('background-image:url()')
    test.ui.ButtonPic.setStyleSheet('background-image:url()')
    test.ui.ButtonSavePic.setStyleSheet('background-image:url()')
    test.ui.ButtonSaveAru.setStyleSheet('background-image:url()')
    test.ui.ButtonLogin.setStyleSheet('background-image:url()')
    test.ui.ButtonCreate.setStyleSheet('background-image:url()')
    test.ui.ButtonStop.setStyleSheet('background-image:url()')
    test.ui.lineEdit.setStyleSheet('background-image:url()')
    test.ui.label_3.setStyleSheet('background-image:url()')
    test.ui.label_4.setStyleSheet('background-image:url()')
    test.ui.lineUser.setStyleSheet('background-image:url()')
    test.ui.linePassWord.setStyleSheet('background-image:url()')
    test.ui.textBrowser.setStyleSheet('background-image:url()')
    test.ui.spinBox.setStyleSheet('background-image:url()')

    app.exec_()                                                            # 程序退出
