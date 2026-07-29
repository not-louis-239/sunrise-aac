# module for error logging

# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import traceback
from datetime import datetime

from sunrise.core.paths import LOGS_DIR

ERR_LOG_FILE = LOGS_DIR / "err.log"

def write_error_log(err: Exception) -> None:
    date_str = datetime.now().isoformat()
    err_str = traceback.format_exc()

    print(f"Fatal exception occurred in program @ {date_str}: \033[91m\033[1m{type(err).__name__}\033[0m\n", file=sys.stderr)
    print(err_str, file=sys.stderr)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ERR_LOG_FILE, 'a', encoding='utf-8') as err_log:
        err_log.write(f"Error at {date_str}\n\n{err_str}\n")

def _test():
    try:
        raise TypeError("Test error")
    except TypeError as exc:
        write_error_log(exc)

if __name__ == "__main__":
    _test()
