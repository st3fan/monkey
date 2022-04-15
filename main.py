# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/


import os
import monkey.repl as repl


def main():
    print(f"Hello {os.getlogin()}! This is the Monkey programming language!")
    print("Feel free to type in some code")
    repl.start()


if __name__ == "__main__":
    main()
