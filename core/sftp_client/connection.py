import os
import paramiko
from dotenv import load_dotenv

# Load .env once
load_dotenv()

HOST = os.getenv("SFTP_HOST", "127.0.0.1")
PORT = int(os.getenv("SFTP_PORT", "3373"))
USER = os.getenv("SFTP_USER")
PASS = os.getenv("SFTP_PASS")


def get_sftp_client():
    """
    Creates a Paramiko Transport and returns an SFTPClient.
    Mirrors the logic already used in sftp_agent.py.
    """
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USER, password=PASS)

    sftp = paramiko.SFTPClient.from_transport(transport)

    # Attach transport so the runner can close both cleanly
    sftp._transport = transport
    return sftp
