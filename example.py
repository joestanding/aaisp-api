#!/usr/bin/env python3

import os
from aaisp import AAISP

# --------------------------------------------------------------------------- #

def main():

    print("-------------------------")
    print("AAISP Lines")
    print("-------------------------\n")

    username = os.environ.get('AAISP_USERNAME')
    password = os.environ.get('AAISP_PASSWORD')

    if not username or not password:
        print("Environment variables AAISP_USERNAME and AAISP_PASSWORD " \
              "must be set!")
        return False

    aaisp = AAISP(username, password)

    for service_id in aaisp.services():
        tx_rate = aaisp.tx_rate(service_id, AAISP.FORMAT_MBITS)
        rx_rate = aaisp.rx_rate(service_id, AAISP.FORMAT_MBITS)

        usage_rem  = aaisp.usage_remaining(service_id, AAISP.FORMAT_GBYTES)
        usage_used = aaisp.usage_used(service_id, AAISP.FORMAT_GBYTES)
        login      = aaisp.login(service_id)

        print(f"Login: {login}")
        print(f"  Download:  {tx_rate} Mbit/s")
        print(f"  Upload:    {rx_rate} Mbit/s")
        print(f"  Remaining: {usage_rem} GB")
        print(f"  Used:      {usage_used} GB\n")

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
