import subprocess
import csv
import io

class RemoteControl:
    @staticmethod
    def send_message(target, message):
        """
        target: IP or Hostname
        message: The message string
        """
        try:
            # target * is for all users on that machine
            cmd = f'msg /server:{target} * "{message}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout or result.stderr
        except Exception as e:
            return False, str(e)

    @staticmethod
    def shutdown(target, restart=False, force=True, time=0):
        """
        target: IP or Hostname
        """
        try:
            flag = "/r" if restart else "/s"
            force_flag = "/f" if force else ""
            cmd = f'shutdown {flag} {force_flag} /t {time} /m \\\\{target}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout or result.stderr
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_processes(target):
        """
        target: IP or Hostname
        Returns list of dicts: [{'name': ..., 'pid': ..., 'mem': ...}, ...]
        """
        try:
            cmd = f'tasklist /S {target} /FO CSV /NH'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr

            processes = []
            f = io.StringIO(result.stdout.strip())
            reader = csv.reader(f)
            for parts in reader:
                if len(parts) >= 2:
                    processes.append({
                        'name': parts[0],
                        'pid': parts[1],
                        'session_name': parts[2],
                        'mem': parts[4]
                    })
            return True, processes
        except Exception as e:
            return False, str(e)

    @staticmethod
    def kill_process(target, pid):
        try:
            cmd = f'taskkill /S {target} /PID {pid} /F'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout or result.stderr
        except Exception as e:
            return False, str(e)
