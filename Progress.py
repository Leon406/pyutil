import re

import sys
import time

class ProgressBar:
    def __init__(self, count=0, total=0, width=50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1

    def log(self, s):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()

        progress = self.width * self.count / self.total
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('#' * int(progress) + '-' * int((self.width - progress)) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()


import urllib.parse

attach = r'attachment;filename="___.mp4";filename*=UTF-8\'\'%E7%AC%AC%E4%B8%80%E7%AB%A0.mp4'
print(urllib.parse.unquote(attach))
r = re.search(r"""attachment;filename="(.+)";filename\*=UTF-8\\'\\'(.+)?""", urllib.parse.unquote(attach))

print(r.group(r.lastindex))

# bar = ProgressBar(total = 10)
# for i in range(10):
#     bar.move()
#     bar.log('We have arrived at: ' + str(i + 1))
#     time.sleep(1)
