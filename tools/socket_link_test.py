"""Exercise the host-to-robot socket link by hand.

Stands up the same TCP server ``control_center.py`` uses, but drives it
interactively: press Enter to push a route string to the robot, and respond to
its status messages yourself. Useful for checking the WiFi link and the
firmware's route parsing without running a full mission.
"""

import os
import socket

HOST_IP = os.environ.get("GEOGUIDE_HOST_IP", "192.168.137.181")
HOST_PORT = int(os.environ.get("GEOGUIDE_HOST_PORT", 8002))

# Sample routes to push at the robot, in the format the firmware expects.
paths = ["SSRS", "RR", "SRSLSRSL"]
emergency = "e"


def send(conn, message):
    conn.sendall(str.encode(str(message)))
    print("sent:", message)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST_IP, HOST_PORT))
        s.listen()
        print("waiting for the robot to connect...")
        conn, addr = s.accept()

        with conn:
            print("connected to {addr}".format(addr=addr))
            input("press enter to send the first path ")
            send(conn, paths[0])

            while True:
                message = conn.recv(1024).decode()
                print("received:", message)

                if message == "ready":
                    input("press enter to send the stop signal ")
                    send(conn, emergency)
                elif message == "send":
                    send(conn, paths[1])


if __name__ == "__main__":
    main()
