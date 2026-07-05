"""Monthly: portfolio digest email to profiles with email_digest = true.
Implemented in M4.

Run: backend/.venv/Scripts/python.exe -m workers.jobs.send_digests
"""

import sys


def main() -> int:
    print("send_digests: not implemented until M4 (digest email)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
