# text = 'add Leha, loh'
# first_split = text.split(', ')
# first_word = first_split[0].split()[1]
# second_word = first_split[1]
#
# print(first_split, '\n', first_word, '\n', second_word)

class Adres:
    def out(self):
        return "out def"

class sec_Adres(Adres):
    def sec_out(self):
        return self.out()

def main():
    instance = sec_Adres()
    result = instance.sec_out()
    print(result)

if __name__ == "__main__":
    main()
