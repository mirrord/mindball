#!/usr/bin/env python

from mindwave import Headset

if __name__ == "__main__":
    for port in range(9):
        try:
            h = Headset(f"COM{port}")
            h.disconnect()
        except Exception:
            pass
    print("done")
