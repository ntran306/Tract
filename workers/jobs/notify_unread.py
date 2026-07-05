"""Every 15 min: email users with unread messages older than ~15 minutes
(mirroring), respecting profiles.email_mirror. Implemented in M4.

Run: backend/.venv/Scripts/python.exe -m workers.jobs.notify_unread
"""

import sys


def main() -> int:
    print("notify_unread: not implemented until M4 (email mirroring)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
