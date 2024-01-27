# Andrews & Arnold CHAOS API Library
A quick Python library to retrieve line information such as TX and RX speeds, usage quotas, and other information.

Example:
```python
from aaisp import AAISP

# Provide A&A log-in credentials
aaisp = AAISP('<aaisp_control_username>', '<aaisp_control_password>')

# Enumerate available lines and retrieve their numerical IDs
services = aaisp.services()

# Print basic information for each available line
for service in services:
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
```
