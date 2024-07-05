import os
import paramiko
import stat

HOSTNAME='192.168.0.13'
USERNAME='ft'
PASSWORD='fischertechnik'


def main():
    ssh = paramiko.SSHClient() 
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    sftp = ssh.open_sftp()
    try:
        sftp.put('scripts/root.c', '/opt/ft/root.c')
    except: 
        pass
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command('gcc root.c -o root')
    # Print the output of the command
    print(stdout.read().decode())

    # Print any error messages from the command
    print(stderr.read().decode())

    ssh.close()

if __name__ == '__main__':
    main()