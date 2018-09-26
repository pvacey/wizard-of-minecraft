import mcrcon

# python 2 compatibility
try: input = raw_input
except NameError: pass


def main(host, port, password):
    rcon = mcrcon.MCRcon()
    print("# connecting to %s:%i..." % (host, port))
    rcon.connect(host, port, password)
    print("# ready")
    #response = rcon.command('/kick vaks0731')
    response = rcon.command('/stop')
    print(response)
    print("# done")

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) != 3:
        print("usage: python demo.py <host> <port> <password>")
        sys.exit(1)
    host, port, password = args
    port = int(port)
    main(host, port, password)
