import json
import requests
from web3 import Web3, IPCProvider
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

QUICKNODE_ENDPOINT = os.environ.get("QUICKNODE_PROVIDER")
w3 = Web3(Web3.HTTPProvider(QUICKNODE_ENDPOINT))


def handle_event(event):
    print(event.hex())
    # and whatever


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)


def main():
    tx_filter = w3.eth.filter("pending")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(log_loop(tx_filter, 2)))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
