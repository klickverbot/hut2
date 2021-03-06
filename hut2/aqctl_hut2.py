#!/usr/bin/env python3

import argparse
import logging
import sys
import asyncio

from . import HUT2

from artiq.protocols.pc_rpc import Server
from artiq.tools import (verbosity_args, simple_network_args, init_logger,
                         bind_address_from_args)


logger = logging.getLogger(__name__)


def get_argparser():
    parser = argparse.ArgumentParser(
        description="""HUT2 controller.
        Use this controller for Anel HUT2 power distribution devices.""")
    parser.add_argument(
        "-d", "--device", default=None,
        help="Device host name or IP address.")
    simple_network_args(parser, 3271)
    verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    init_logger(args)

    if args.device is None:
        print("You need to supply a -d/--device "
              "argument. Use --help for more information.")
        sys.exit(1)

    loop = asyncio.get_event_loop()

    async def run():
        with await HUT2.connect(args.device, loop=loop) as dev:
            server = Server({"hut2": dev}, None, True)
            await server.start(bind_address_from_args(args), args.port)
            try:
                await server.wait_terminate()
            finally:
                await server.stop()

    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()
