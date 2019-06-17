def paragraph_dividing(message):
    charlist = list(message)
    i=0
    while(True):
        if i > len(charlist) - 1:
            break
        if charlist[i] == '\n' and i < len(charlist)-1:
            charlist.insert(i+1, '\r')
            charlist.insert(i+2, '\n')
            i += 3
            continue
        i += 1
    return ''.join(charlist)

# if __name__ == '__main__':
#     message = '这里是'+'\r'+'\n'+'宿舍'+'\r'+'\n'+'吗'
#     print(message)
#     message = paragraph_dividing(message)
#     print(message)