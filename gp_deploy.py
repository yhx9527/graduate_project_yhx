from config import SSH_IP, SSH_PWD, SSH_USERNAME
import paramiko
import os
from os.path import join
cur_file_path = os.path.abspath(os.path.dirname(__file__))


class MySSH(object):
    def __init__(self, host, username, pwd):
        self.host = host
        self.username = username
        self.pwd = pwd
        self.ssh = None
        self.sftp = None
        self.ssh_connect()
        self.sftp_open()
    def ssh_connect(self):
        try:
            print('连接SSH...')
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #允许连接不在know_hosts文件中的主机
            self.ssh.connect(self.host, 22, username=self.username, password=self.pwd)

            print('连接SSH 成功...')
        except Exception as ex:
            print('连接ssh出错',ex)

    def sftp_open(self):
        print('打开SFTP 成功...')
        self.sftp = self.ssh.open_sftp()

    def sftp_put(self, from_path, to_path):
        '''
            上传文件到远程服务器
        '''
        return self.sftp.put(from_path, to_path)

    def sftp_get(self, from_path, to_path):
        '''
            从远程服务器下载文件
        '''
        return self.sftp.get(from_path, to_path)

    def exc(self, cmd):
        '''
            让远程服务器执行cmd
        '''
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        print('执行%s:' % cmd)
        for line in stdout.readlines():
            print(line)
        for line in stderr.readlines():
            print(line)


    def close(self):
        self.sftp.close()
        self.ssh.close()
        print('关闭SSH连接...成功')

    def __del__(self):
        self.close()


def upload_deploy():
    myssh = MySSH(SSH_IP, SSH_USERNAME, SSH_PWD)
    enter_project = 'cd /home/yuhanxiang/graduate_project_yhx &&'

    #上传配置文件
    print('上传配置文件')
    myssh.sftp_put(join(cur_file_path, 'config_production.py'), join('/','home','yuhanxiang', 'graduate_project_yhx', 'config.py'))
    print('git拉取新代码')
    myssh.exc(enter_project+'git pull')
    #启动服务
    app_cmd = 'supervisorctl restart svdca_app svdca_celery_beat svdca_celery'
    myssh.exc(app_cmd)

if __name__ == '__main__':
    upload_deploy()