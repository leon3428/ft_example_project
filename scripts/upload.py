import os
import paramiko
import stat

HOSTNAME='192.168.0.13'
USERNAME='ft'
PASSWORD='fischertechnik'

def copy_helper(sftp: paramiko.SFTPClient, src: str, dest: str):
    sftp.mkdir(dest)
    
    for item in os.listdir(src):
        local_item = os.path.join(src, item)
        remote_item = os.path.join(dest, item)

        if os.path.isdir(local_item):
            copy_helper(sftp, local_item, remote_item)
        else:
            sftp.put(local_item, remote_item)

def delete_helper(sftp: paramiko.SFTPClient, path: str):
    for item in sftp.listdir_attr(path):
        remote_item = os.path.join(path, item.filename)
        if stat.S_ISDIR(item.st_mode):
            delete_helper(sftp, remote_item)
        else:
            sftp.remove(remote_item)

    sftp.rmdir(path)

def upload(sftp: paramiko.SFTPClient, project_name: str, dest: str):
    delete_helper(sftp, os.path.join(dest, project_name))

    copy_helper(sftp, project_name, os.path.join(dest, project_name))

def main():
    ssh = paramiko.SSHClient() 
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    sftp = ssh.open_sftp()

    upload(sftp, 'ft_example', '/opt/ft/workspaces')
    
    sftp.close()
    ssh.close()

if __name__ == '__main__':
    main()