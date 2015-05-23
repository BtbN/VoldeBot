#!/usr/bin/env python2

from voldebot import MarkovBot
import sys
import re

class FakeConn:
    nick = "voldebot"

    def register_callbacks(*args, **kwargs):
        return

fake_conn = FakeConn()
bot = MarkovBot(fake_conn)

prog1 = re.compile(r'^\[\d\d:\d\d:\d\d\]\s+\*\*\*.*$', re.IGNORECASE)
prog2 = re.compile(r'^\[\d\d:\d\d:\d\d\]\s+(<.*?>|\*\s.+?)\s', re.IGNORECASE)

counter = 0
last_print = 0
print_step = 10000

for arg in sys.argv[1:]:
    try:
        print("Reading file %s" % arg)

        for line in open(arg):
            line = line.strip()

            if prog1.match(line):
                continue

            line = prog2.sub('', line).strip()

            bot.parse_message(line)

            counter += 1

            if counter >= last_print + print_step:
                print("Parsed %s messages" % counter)
                last_print = counter
    except IOError:
        print("Failed reading from %s" % arg)

