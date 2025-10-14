# -------------- UTILITY TO CHECK SERVER AVAILABILITY -------------------------#
#
# host = "10.0.3.172"
# ping_count = 2
# testNetworkConn([host], ping_count)
#
# -----------------------------------------------------------------------------#

from re import findall
from subprocess import Popen, PIPE
from typing import TYPE_CHECKING


def testNetworkConn(host, ping_count):
    for ip in host:
        data = ""+'\n'
        output = Popen(f"ping {ip} -n {ping_count}", stdout=PIPE, encoding="utf-8")

        for line in output.stdout:
            data = data + line
            ping_test = findall("TTL", data)

        if ping_test:
            print(f"\nSQL Server: OSI Layer connectivity .. OK.")
            sol = True
            # print(sol)
        else:
            print(f"{ip} : Critical Error, Ping failure...")
            sol = False

    return sol

