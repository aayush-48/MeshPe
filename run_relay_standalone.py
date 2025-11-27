import socket
import logging
import time

# --- CONFIGURATION ---
# REPLACE THIS WITH THE MAC ADDRESS OF THE BANK (DEVICE B)
BANK_MAC_ADDRESS = "PUT_BANK_MAC_HERE" 
RFCOMM_CHANNEL = 4

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("RelayNode")

def forward_to_bank(data: bytes) -> bool:
    """
    Connects to the Bank Node and forwards the data.
    """
    if BANK_MAC_ADDRESS == "PUT_BANK_MAC_HERE":
        logger.error("CRITICAL: BANK_MAC_ADDRESS not set in run_relay_standalone.py")
        return False

    logger.info(f"[Relay] Forwarding {len(data)} bytes to Bank ({BANK_MAC_ADDRESS})...")
    
    try:
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.connect((BANK_MAC_ADDRESS, RFCOMM_CHANNEL))
        sock.send(data)
        sock.close()
        logger.info("[Relay] Forwarded successfully!")
        return True
    except Exception as e:
        logger.error(f"[Relay] Forwarding failed: {e}")
        return False

def run_relay():
    logger.info("[Relay] Starting Relay Node (RFCOMM)...")
    
    if BANK_MAC_ADDRESS == "PUT_BANK_MAC_HERE":
        logger.warning("WARNING: You must set BANK_MAC_ADDRESS in this file to forward packets!")

    try:
        # Create Server Socket
        server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        server_sock.bind((socket.BDADDR_ANY, RFCOMM_CHANNEL))
        server_sock.listen(1)

        logger.info(f"[Relay] Listening on Channel {RFCOMM_CHANNEL}...")
        logger.info("[Relay] Waiting for Sender...")

        while True:
            client_sock, address = server_sock.accept()
            logger.info(f"Accepted connection from Sender: {address}")

            try:
                # Receive Data
                full_data = b""
                while True:
                    chunk = client_sock.recv(4096)
                    if not chunk:
                        break
                    full_data += chunk
                
                if full_data:
                    logger.info(f"Received {len(full_data)} bytes from Sender.")
                    
                    # FORWARD TO BANK
                    success = forward_to_bank(full_data)
                    
                    if success:
                        logger.info("Packet Relayed Successfully.")
                    else:
                        logger.error("Failed to Relay Packet.")
                        
            except Exception as e:
                logger.error(f"Error handling connection: {e}")
            finally:
                client_sock.close()
                logger.info("Sender connection closed.\n")

    except OSError as e:
        if e.winerror == 10050:
            logger.error("CRITICAL: Bluetooth Adapter is OFF.")
        else:
            logger.error(f"Relay crashed: {e}")
    except Exception as e:
        logger.error(f"Relay crashed: {e}")
    finally:
        if 'server_sock' in locals():
            server_sock.close()

if __name__ == "__main__":
    run_relay()
