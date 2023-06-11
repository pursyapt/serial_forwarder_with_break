import argparse
import logging
import socket
import time

import serial


def parse_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--host",
                        help="IP Address to listen for connections on",
                        default="0.0.0.0")
    parser.add_argument("--port",
                        help="TCP Port which the program should listen for incoming connections on, e.g. 5000",
                        required=True,
                        type=int)
    parser.add_argument("--device",
                        help="Physical device on machine which should be forwarded, e.g. /dev/ttyAMA1",
                        required=True)
    parser.add_argument("--baud",
                        help="Baud rate which should be used to communicate over the raw serial port",
                        default=115200,
                        type=int)
    parser.add_argument("--break-delay",
                        help="How long to wait (in ms) once a new connection comes in until we send the break",
                        default=10,
                        type=int)
    parser.add_argument("--break-length",
                        help="How long (in ms) the break pulse should last on the UART",
                        default=10,
                        type=int)

    return parser.parse_args()


def main():
    args = parse_arguments()

    logging.basicConfig(level=logging.DEBUG)

    logging.info("Serial Port Forwarder with Break V1.0 starting up")

    logging.info(f"Opening serial port on {args.device} at baud rate {args.baud}")

    ser = serial.Serial(
        port=args.device,
        baudrate=args.baud,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1/1000
    )

    logging.info(f"Starting to listen on port {args.port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((args.host, args.port))
        s.listen()
        conn, addr = s.accept()
        try:
            logging.info(f"Connected by {addr}")
            logging.debug(f"Starting initial delay of {args.break_delay}ms before break")
            time.sleep(args.break_delay / 1000)
            logging.debug(f"Sending break pulse of {args.break_length}ms")
            ser.send_break(args.break_length / 1000)

            data = ser.read(1024)

            logging.debug(f"Received the following during the break: {data}")

            conn.sendall(data)

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                logging.debug(f"-> {data}")

                data = ser.read(1024)

                if data:
                    logging.debug(f"<- {data}")
                    conn.sendall(data)
        finally:
            logging.info(f"Closing connection from {addr}")
            conn.close()


if __name__ == "__main__":
    main()
