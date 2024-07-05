import os
import paramiko

HOSTNAME='192.168.0.13'
USERNAME='ft'
PASSWORD='fischertechnik'

def main():
    ssh = paramiko.SSHClient() 
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    sftp = ssh.open_sftp()
    try:
        sftp.put('scripts/opencv-4.1.0-armhf.tar.bz2', '/opt/ft/opencv-4.1.0-armhf.tar.bz2')
    except: 
        pass

    try:
        sftp.put('scripts/install_opencv.sh', '/opt/ft/install_opencv.sh')
        sftp.chmod('/opt/ft/install_opencv.sh', 0o777)
    except: 
        pass

    sftp.close()
    ssh.close()

if __name__ == '__main__':
    main()