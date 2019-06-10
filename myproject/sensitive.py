# -*- coding:utf-8 -*-

# DFA算法
class DFAFilter(object):
    def __init__(self):
        self.keyword_chains = {}  # 关键词链表
        self.delimit = '\x00'  # 限定

    def add(self, keyword):
        keyword = keyword.lower()  # 关键词英文变为小写
        chars = keyword.strip()  # 关键字去除首尾空格和换行
        if not chars:  # 如果关键词为空直接返回
            return
        level = self.keyword_chains
        # 遍历关键字的每个字
        i = 0
        for i in range(len(chars)):
            # 如果这个字已经存在字符链的key中就进入其子字典
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                last_level, last_char = list(), list()
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())
            f.close()
        # print(self.keyword_chains)
        f = open("./templates/sensitive_dict.txt","w")
        f.write(str(self.keyword_chains))
        f.close()

    @staticmethod
    def filter(_message, repl="*"):
        if not _message:
            return _message
        f = open("./templates/sensitive_dict.txt", "r")
        data = f.read()
        keyword_chains = eval(data)
        f.close()
        message = _message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if '\x00' not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)

if __name__ == "__main__":
    sensitive = DFAFilter()
    path = "./templates/sensitive.txt"
    sensitive.parse(path)

    '''
    message = "傻逼！！孙笑川"
    result = DFAFilter.filter(message)
    print(message)
    print(result)
    '''



