# Serial Forwarder with Break
This project was created to solve a problem with forwarding a serial port over a network connection.
Specifically, I needed to allow a remote machine to interact with a local serial port but also send a UART break at
the beginning of the connection to force the connected device into a specific mode.

See this Stack Overflow post for more details:- https://stackoverflow.com/questions/76447605/sending-break-over-socat-ssh-connection