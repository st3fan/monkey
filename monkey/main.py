#!/usr/bin/env python3


import os
import monkey.repl as repl


def main():
    print(f"Hello {os.getlogin()}! This is the Monkey programming language!")
    print("Feel free to type in some code")
    repl.start()


if __name__ == "__main__":
    main()
