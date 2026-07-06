import sys
import os
import markdown2
import winreg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextBrowser, QCheckBox, QPushButton,
                             QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class AutoTipsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadMarkdown()
        self.loadAutoStartState()
        
    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle('seewo一体机使用指北')
        self.setWindowIcon(QIcon('icon.ico'))
        
        # 设置窗口大小
        self.resize(800, 600)
        
        # 窗口居中显示
        screen_geometry = QDesktopWidget().screenGeometry()
        self.move(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2
        )
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建文本浏览器用于显示Markdown
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setFont(QFont("微软雅黑", 10))
        main_layout.addWidget(self.text_browser)
        
        # 创建底部布局
        bottom_layout = QHBoxLayout()
        
        # 创建"在开机时显示"复选框
        self.auto_start_checkbox = QCheckBox("在开机时显示")
        self.auto_start_checkbox.stateChanged.connect(self.toggleAutoStart)
        bottom_layout.addWidget(self.auto_start_checkbox)
        
        # 添加弹性空间
        bottom_layout.addStretch()
        
        # 创建"编辑提示"按钮
        self.edit_button = QPushButton("编辑显示内容")
        self.edit_button.clicked.connect(self.openMarkdownFile)
        bottom_layout.addWidget(self.edit_button)
        
        main_layout.addLayout(bottom_layout)
        
    def getMarkdownFilePath(self):
        """获取Markdown文件路径"""
        # 扩展环境变量%USERPROFILE%
        user_profile = os.environ.get('USERPROFILE', '')
        if not user_profile:
            user_profile = os.path.expanduser('~')
        
        # 构建完整路径
        docs_path = os.path.join(user_profile, 'Documents', 'auto_tips')
        os.makedirs(docs_path, exist_ok=True)
        
        file_path = os.path.join(docs_path, 'readme.md')
        return file_path
    
    def loadMarkdown(self):
        """加载并显示Markdown文件"""
        file_path = self.getMarkdownFilePath()
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # 将Markdown转换为HTML
                html_content = markdown2.markdown(markdown_content)
                
                # 设置HTML内容
                self.text_browser.setHtml(html_content)
            else:
                # 如果文件不存在，创建默认内容
                default_content = "# 自动提示\n\n欢迎使用自动提示程序！\n\n请在此处编辑您的提示内容。"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                
                html_content = markdown2.markdown(default_content)
                self.text_browser.setHtml(html_content)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载Markdown文件：{str(e)}")
    
    def getAutoStartCommand(self):
        """获取自启动命令"""
        # 获取当前脚本路径
        script_path = os.path.abspath(__file__)
        
        # 检查是否被打包成exe
        if getattr(sys, 'frozen', False):
            # 如果是打包的exe，使用sys.executable
            return sys.executable
        else:
            # 如果是Python脚本，使用Python解释器运行脚本
            python_exe = sys.executable
            return f'"{python_exe}" "{script_path}"'
    
    def loadAutoStartState(self):
        """加载自启动状态"""
        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            
            # 尝试读取值
            try:
                registry_value, _ = winreg.QueryValueEx(key, "AutoTips")
                # 获取当前的自启动命令
                current_command = self.getAutoStartCommand()
                
                # 比较注册表中的值与当前命令
                if registry_value == current_command:
                    self.auto_start_checkbox.setChecked(True)
                else:
                    self.auto_start_checkbox.setChecked(False)
            except FileNotFoundError:
                # 键值不存在
                self.auto_start_checkbox.setChecked(False)
            
            winreg.CloseKey(key)
            
        except Exception as e:
            print(f"读取注册表时出错：{e}")
            self.auto_start_checkbox.setChecked(False)
    
    def toggleAutoStart(self, state):
        """切换自启动状态"""
        try:
            # 打开注册表键（可写）
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            )
            
            if state == Qt.Checked:
                # 添加自启动项
                auto_start_command = self.getAutoStartCommand()
                winreg.SetValueEx(key, "AutoTips", 0, winreg.REG_SZ, auto_start_command)
                # QMessageBox.information(self, "提示", "已启用开机自启动")
            else:
                # 删除自启动项
                try:
                    winreg.DeleteValue(key, "AutoTips")
                    # QMessageBox.information(self, "提示", "已禁用开机自启动")
                except FileNotFoundError:
                    # 值不存在，无需处理
                    pass
            
            winreg.CloseKey(key)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修改自启动设置时出错：{str(e)}")
    
    def openMarkdownFile(self):
        """打开Markdown文件进行编辑"""
        file_path = self.getMarkdownFilePath()
        
        try:
            # 确保文件存在
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("# 使用指南\n\n在文档文件中的auto_tips文件夹下的readme.md文件中编辑显示内容，支持Markdown格式。")
            
            # 使用默认程序打开文件
            os.startfile(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件：{str(e)}")


def main():
    app = QApplication(sys.argv)
    window = AutoTipsApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()