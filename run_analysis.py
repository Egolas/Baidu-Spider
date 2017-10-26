import jieba
import re
jieba.load_userdict('word_list.txt')
with open('file.txt', 'r', encoding="utf-8") as f:
    with open('out.txt', 'w', encoding="utf-8") as out_file:
        file_text = f.read()
        seg_list = jieba.cut(file_text)
        frequency_list = {}
        for word in seg_list:
            if not re.match(r"[\-:《》，。‘“”’：；●▲【】■·、？！%!@#%^&*()={};'/.,?<>:'|[\]~`A-Z0-9\s]+", word):
                if word in frequency_list:
                    frequency_list[word] += 1
                    pass
                else:
                    frequency_list[word] = 1
                    pass

        items = sorted(frequency_list.items(), key=lambda d: d[1], reverse=True)
        for (word, frequency) in items:
            out_file.write(word + "/" + str(frequency) + "  ")
            pass
