import socket
import time

LOGIN = b'#L#2.0;860000000000000;NA;46D4\r\n'
DATA = (
    b'#D#010125;112233;5128.199596;N;00000.122544;E;0;0;0;0;0;0;NA;;NA;'
    b'example1:1:0,example2:2:0.12,example3:1:123;72D3\r\n'
)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.sendto(LOGIN, ('127.0.0.1', 50_000))
    answer, _ = sock.recvfrom(64)
    print('Login packet answer', answer)

    try:
        while True:
            sock.sendto(DATA, ('127.0.0.1', 50_000))
            answer, _ = sock.recvfrom(64)

            if answer == b'server_off\r\n':
                print('Server off')
                break

            print('Data packet answer', answer)

            time.sleep(5)
    except KeyboardInterrupt as e:
        print('Stop sending data')

    sock.close()


if __name__ == '__main__':
    main()
