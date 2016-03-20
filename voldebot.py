#!/usr/bin/env python2

import random
import re
import redis
import time

from irc import IRCBot, run_bot
from twitch_emotes import translate_emote
import distdata


class MarkovBot(IRCBot):
    chain_length = 2
    chattiness = 0
    max_words = 30
    messages_to_generate = 5
    prefix = 'irc'
    separator = '\x01'
    stop_word = '\x02'
    filter_exps = [r'fuck', r'bitch', r'bitches', r'^http.*', r'^www.*']
    active_channels = distdata.active_channels
    unlimited_channels = distdata.unlimited_channels
    channel_timers = dict()
    cooldown = 60

    def __init__(self, *args, **kwargs):
        super(MarkovBot, self).__init__(*args, **kwargs)
        self.redis_conn = redis.Redis()

        self.filter_regs = []
        for exp in self.filter_exps:
            self.filter_regs.append(re.compile(exp, re.I))

    def make_key(self, k):
        return '-'.join((self.prefix, k))

    def sanitize_message(self, message):
        return re.sub('[\"\']', '', message.lower())

    def split_message(self, message):
        words = message.split()
        
        if len(words) > self.chain_length:
            words.append(self.stop_word)

            for i in range(len(words) - self.chain_length):
                yield words[i:i + self.chain_length + 1]

    def is_bad_word(self, word):
        word = word.strip()
        for reg in self.filter_regs:
            if reg.match(word):
                return True
        return False

    def generate_message(self, seed):
        key = seed
        gen_words = []
        
        for i in xrange(self.max_words):
            words = key.split(self.separator)
            gen_words.append(translate_emote(words[0]))

            next_word = self.redis_conn.srandmember(self.make_key(key))

            counter = 0

            while next_word and self.is_bad_word(next_word):
                if counter > 100:
                    next_word = None
                else:
                    next_word = self.redis_conn.srandmember(self.make_key(key))
                counter += 1

            if not next_word:
                break

            key = self.separator.join(words[1:] + [next_word])

        return ' '.join(gen_words)

    def parse_message(self, message, say_something=False):
        messages = []

        for words in self.split_message(self.sanitize_message(message)):
            key = self.separator.join(words[:-1])
            self.redis_conn.sadd(self.make_key(key), words[-1])
            if say_something:
                best_message = ''
                for i in range(self.messages_to_generate):
                    generated = self.generate_message(seed=key)
                    if len(generated) > len(best_message):
                        best_message = generated
                    if best_message:
                        messages.append(best_message)

        return messages

    def log(self, sender, message, channel):
        say_something = self.is_ping(message) or (sender != self.conn.nick and random.random() < self.chattiness)

        if channel not in self.active_channels and sender != 'oromit':
            say_something = False

        if message.startswith('/'):
            return

        if self.is_ping(message):
            message = self.fix_ping(message)

        messages = self.parse_message(message, say_something)

        if len(messages) and (channel not in self.channel_timers or channel in self.unlimited_channels or time.time() - self.channel_timers[channel] > self.cooldown):
            self.channel_timers[channel] = time.time()
            resmsg = random.choice(messages)
            print("In #%s: <%s> %s" % (channel, sender, message))
            print("-> %s" % resmsg)
            return resmsg

    def command_patterns(self):
        return (('.*', self.log),)

if __name__ == "__main__":
    run_bot(MarkovBot, 'irc.chat.twitch.tv', 6667, distdata.nick, distdata.join_channels, distdata.password)

