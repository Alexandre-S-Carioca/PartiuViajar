import socket

def check_port(host, port):
    print(f"Testing {host}:{port}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        print(f"-> PORT {port} is OPEN!")
        s.close()
    except Exception as e:
        print(f"-> PORT {port} is CLOSED or unreachable: {e}")

if __name__ == "__main__":
    check_port("192.168.0.150", 5432)
    check_port("192.168.0.150", 6379)
