import os
import paramiko

from paramiko import SFTPServerInterface, SFTPServer, SFTPAttributes, RSAKey, Transport, SFTPHandle, ServerInterface
import socket
import threading
from dotenv import load_dotenv

# main.py or server.py logic
import uuid

# from s3_storage import S3Storage  <-- Commented out until you have boto3 installed
from storage.local_storage import LocalStorage
from core.observability.logger import logger
from core.deterministic_layer.hasher import hash_file


load_dotenv()

# --- THE SWITCH LOGIC ---
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "LOCAL")

if STORAGE_TYPE == "S3":
    # storage = S3Storage(...)  # We'll activate this when you're ready for MinIO
    logger.info(f"storage {STORAGE_TYPE} Not set.")
    pass 
else:
    # Use the 80GB on your laptop via LocalStorage
    storage = LocalStorage(base_path="./sftp_root")

logger.info(f"System initialized with {STORAGE_TYPE} storage.")

# 1. Setup the storage adapter (Ground Reality: Local Disk for now)
storage = LocalStorage(base_path="./sftp_root")

# 2. Example of the "Salty" Logger in action
# We create a correlation_id for the start of the session
session_id = str(uuid.uuid4())


def handle_upload(file_name, data):
    # Log with the correlation ID so AI can track this specific event
    logger.info(f"Incoming upload request for {file_name}", extra={"correlation_id": session_id})
    
    # Use the 'Programmable Plumbing' (ABC) to save
    success = storage.save(file_name, data)
    
    if success:
        logger.info(f"Upload completed successfully: {file_name}", extra={"correlation_id": session_id})
    else:
        logger.error(f"Upload failed: {file_name}", extra={"correlation_id": session_id})

from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()
# Use them as variables
USER = os.getenv("SFTP_USER")
PASS = os.getenv("SFTP_PASS")
PORT = int(os.getenv("SFTP_PORT", 3373))

# 1. Setup local storage
KEY_FILE = "sftp_server.key"

# Ensure the storage directory exists and is a directory
if not os.path.isdir(storage.base_path):
    logger.info(f"📁 Creating storage directory: {storage.base_path}")
    os.makedirs(storage.base_path, exist_ok=True)


class LocalFileHandle(paramiko.SFTPHandle):
    def __init__(self, flags, filename):
        super(LocalFileHandle, self).__init__(flags)
        self.filename = filename 
        try:
            self.fd = os.open(filename, flags | os.O_CREAT, 0o644)
            logger.info(f"📄 File opened: {filename}", extra={"correlation_id": session_id})
        except Exception as e:
            logger.error(f"❌ OS Open Error: {e}", extra={"correlation_id": session_id})
            raise


    def write(self, offset, data):
        try:
            os.lseek(self.fd, offset, os.SEEK_SET)
            os.write(self.fd, data)
            return paramiko.SFTP_OK
        except Exception as e:
            print("WRITE ERROR:", e, flush=True)
            return paramiko.SFTP_FAILURE


    def read(self, offset, char_count):
        try:
            os.lseek(self.fd, offset, os.SEEK_SET)
            return os.read(self.fd, char_count)
        except Exception:
            return paramiko.SFTP_FAILURE

    # --- THIS MUST BE INDENTED TO BE PART OF THE CLASS ---
    def close(self):
        os.close(self.fd)
        
        # SHIELD: Don't hash the hash files!
        if self.filename.endswith(".sha256"):
            return paramiko.SFTP_OK

        try:
            file_hash = hash_file(self.filename)
            # Use a context manager to ensure the .sha256 is CLOSED immediately
            with open(f"{self.filename}.sha256", "w") as f:
                f.write(file_hash)
            
            logger.info(f"✅ Integrity Verified: {os.path.basename(self.filename)}", 
                        extra={"correlation_id": session_id, "sha256": file_hash})
        except Exception as e:
            logger.error(f"⚠️ Hash Failed: {e}")
            
        return paramiko.SFTP_OK
    

    

class AILCDiskInterface(paramiko.SFTPServerInterface):
    def _full_path(self, path):
        path = path.lstrip('/')
        return os.path.join(storage.base_path, path)

    def open(self, path, flags, attr):
        clean_path = path.lstrip('/')
        logger.info(f"📂 SFTP Open Request: {clean_path}", extra={"correlation_id": session_id})
        full_path = os.path.join(storage.base_path, clean_path)
        return LocalFileHandle(flags, full_path)

    def stat(self, path):
        full_path = self._full_path(path)
        try:
            st = os.stat(full_path)
            return paramiko.SFTPAttributes.from_stat(st)
        except FileNotFoundError:
            # Tell Paramiko “no such file” via exception, not return code
            raise IOError("No such file")

    # Many clients call lstat() instead of stat(); make them consistent
    def lstat(self, path):
        return self.stat(path)

    def list_dir(self, path):
        full_path = self._full_path(path)
        try:
            items = []
            for name in os.listdir(full_path):
                item_path = os.path.join(full_path, name)
                st = os.stat(item_path)
                attr = paramiko.SFTPAttributes.from_stat(st)
                attr.filename = name
                items.append(attr)
            return items
        except OSError:
            raise IOError("No such file or directory")
        

# 2. CUSTOM AUTH: No more hidden "admin/admin"
class AILCServerInterface(paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        if username == USER and password == PASS:
            logger.info(f"✅ Auth Success: {username}", extra={"correlation_id": session_id})
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

class MySFTPServer(threading.Thread):
    def __init__(self, host='127.0.0.1', port=3373):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        
        # PERSISTENCE: Load key if exists, otherwise create it
        if os.path.exists(KEY_FILE):
            self.key = paramiko.RSAKey.from_private_key_file(KEY_FILE)
            logger.info("🔑 Loaded existing Host Key.", extra={"correlation_id": session_id})
        else:
            self.key = paramiko.RSAKey.generate(2048)
            self.key.write_private_key_file(KEY_FILE)
            logger.info("🆕 Generated new Host Key.", extra={"correlation_id": session_id})

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        
        logger.info(f"🚀 AILC SFTP Server active on {self.host}:{self.port}", extra={"correlation_id": session_id})

        while True:
            conn, addr = sock.accept()
            transport = paramiko.Transport(conn)
            transport.add_server_key(self.key)
            
            # Use our CUSTOM interface instead of the library Stub
            server = AILCServerInterface() 
            
            # The subsystem still handles the file logic (SFTP protocol)
            transport.set_subsystem_handler('sftp', SFTPServer, AILCDiskInterface)
            transport.start_server(server=server)

if __name__ == "__main__":
    server_thread = MySFTPServer()
    server_thread.daemon = True
    server_thread.start()
    
    import time
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 POC Server Offline.", extra={"correlation_id": session_id})

