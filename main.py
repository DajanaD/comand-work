from collections import UserDict
import datetime
import json
import cmd
import sys
import re
import os


# Загальний клас для визначення логикі полів
class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value
 
    @property               # Перевірку на коректність поля
    def value(self):
        return self.__value

    @value.setter          # Перевірку на коректність поля
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.value)

# Клас для зберігання поля "імені контакту"
class Name(Field):
    pass

#  Клас для зберігання поля "дня народження контакту"
class Birthday(Field):
    @Field.value.setter                # Перевірку на коректність веденого
    def value(self, value: str):
        self.__value = datetime.strptime(value, '%Y.%m.%D').date()

#  Клас для зберігання поля "телефону контакту"
class Phone(Field):
   def __init__(self, value):
        super().__init__(value)
        @Field.value.setter                     # Перевірку на коректність веденого
        def value(self, value: str):
            if len(str(self.value)) == 10 and str(self.value).isdigit():
                self.value = value
            else:
                raise ValueError('Invalid phone number')

#  Відповідає за логіку обробки інформації з обовязкових полів
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = ''
        self.file = 'AddressBook.txt'

    def add_phone(self, phone_number: str):      # додавання в полі "телефон"
        self.phones.append(Phone(phone_number))


    def find_phone(self, phone_number: str):      # пошук в полі "телефон"
        for phone in self.phones:
            if phone.value == phone_number:
                def formatted_numbers():
                    list_numbers = []
                    line_0 = ('|{:^10}|{:^10}|'.format('name', 'phone'))
                    list_numbers.append(line_0)
                    line_1 = '|{:<10}|{:^10}|'. format(self.name.value, phone.value)
                    list_numbers.append(line_1)
                    return list_numbers
                for el in formatted_numbers():
                    print(el)
                return phone

    def edit_phone(self, old_phone, new_phone):       # редагування в полі "телефон"
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError


    def remove_phone(self, phone_number):           # видалення в полі "телефон"
        phone  = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)

    def days_to_birthday(self, birthday):          # повертає кількість днів до наступного дня народження
        if birthday:
            now = datetime.datetime.now()
            then = datetime.datetime.strptime(birthday, '%Y.%m.%D')
            delta1 = datetime.datetime(now.year, then.month, then.day)
            delta2 = datetime.datetime(now.year+1, then.month, then.day)

            result = ((delta1 if delta1 > now else delta2) - now).days
            print(f'{result} days left until birthday')

    def __str__(self):
    
        list_numbers = []
        line_0 = ('|{:^10}|{:^22}|{:^10}|{:^10}|{:^10}|'.format('name', 'phone', 'birthday', 'teg', 'note'))
        list_numbers.append(line_0)
        phon = '; '.join(p.value for p in self.phones)
        line_1 = ('|{:<10}|{:^22}|{:^10}|{:^10}|{:^10}|'. format(self.name.value, phon, self.birthday, "-", "-"))
        list_numbers.append(line_1)
        for el in list_numbers:
           print(el)
       
        return f"done"

#  Клас для зберігання та управління записами
class AddressBook(UserDict):
    def add_record(self, record: Record):       # додавання запису
        self.data[record.name.value] = record
        
        
    def find(self, name: Record):              # пошук запису
        for names in self.data:
            if names == name:
                return self.data[name]
            
            
    def delete(self, name:Record):             # видалення запису
        if self.data.get(name):
            del self.data[name]

    def iterator(self, item_number):         # пагінація(для ситуацій, коли Записи дуже великого обєму і треба показати вміст частинами)
        counter = 0
        result = ''
        for item, record in self.data.items():
            result += f'{item}: {record}'
            counter += 1
            if counter >= item_number:
                yield result
                counter = 0
                result = ''  
    def dump(self):                           # додавання запису в файл     
        with open(self.file, 'wb') as file:
            json.dump((self.record_id, self.record), file)

    def load(self):                         # зчитування запису з файл
        if not self.file.exists():           
            return
        with open(self.file, 'rb') as file:
            self.record_id, self.record = json.load(file)

    def search(self):                       # пошук в запису часткової інформації через ввод із введеного рядка
        info = input()
        info = info.lower()
        for key, value in self.data.items():
            if info in key:
                return self.data[key]
            elif info in value:
                keys = [key for key, values in self.data() if values == value]
                return  keys
            else:
                return f'Not found'

# Контроль що програма не втрачає данні
class Controller(cmd.Cmd):     
    def exit(self):
        self.book.dump()
        return True
    
exit_words = ["good bye", "close", "exit", "bye"]

class NoteActions:
    @staticmethod
    def add_note(notes, name, title):     #додавання нотатків
        notes[name] = title
        return f"Note added: {name}, {title}"

    @staticmethod
    def edit_note(notes, name, new_title):  #редагуваня нотатків
        if name in notes:
            notes[name] = new_title
            return f"Note for {name} edited: {new_title}"
        else:
            return f"Note for {name} not found."

    @staticmethod
    def delete_note(notes, name):    #видалення нотатків
        if name in notes:
            del notes[name]
            return f"Note for {name} deleted."
        else:
            return f"Note for {name} not found."

class NoteManager:
    def __init__(self, exit_words=None):
        self.notes = {}
        self.exit_words = exit_words or []
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.data_file_path = os.path.join(current_directory, "data.txt")
    
def save_notes_to_file(self):   #збереження змін у файлі
        with open(self.data_file_path, "w") as file:
            for name, title in self.notes.items():
                file.write(f"{name}, {title}\n")

def load_notes_from_file(self):
    try:
        with open(self.data_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                name, title = line.strip().split(', ')
                self.notes[name] = title
    except FileNotFoundError:
        pass

def get_note_by_name(self, name):
    if name in self.notes:
        return f"Note for {name}: {self.notes[name]}"
    else:
        return f"Note for {name} not found."
    
book = AddressBook()
note_actions = NoteActions()
def hello():
    return "How can I help you?"

def exit_handler():
    return "Good bye!"

def main():
    while True:
        s = input("...")
        s = s.lower()       
        if s == "hello":
            print(hello())  
            print(hello())
        elif re.search(r'add', s):
            new_text = s.replace("add ", "").split(" ")
            john_record = Record(new_text[0])
            john_record.add_phone(new_text[1])
            book.add_record(john_record)
        elif re.search(r'change', s):
            new_text = s.replace("change ", "").split(" ")
            john = book.find("John")
            john.edit_phone(new_text)
        elif re.search(r'phone', s):
            new_text = s.replace("phone ", "").split(" ")
            found_phone =john.find_phone(new_text[1])
        elif re.search(r'show all', s):  
            for name, record in book.data.items():
                print(record)
        elif s.lower().startswith('add-not'):
            first_split = s.split(', ')
            note_name = first_split[0].split()[1]
            title = first_split[1]
            return note_actions.add_note(self.notes, note_name, title)
        elif s.lower().startswith('edit-not'):
            edit_split = s.split(', ')
            note_name = edit_split[0].split()[1]
            new_title = edit_split[1]
            return note_actions.edit_note(self.notes, note_name, new_title)
        elif s.lower().startswith('delete-not'):
            name_to_delete = s.split(' ')[1]
            return note_actions.delete_note(self.notes, name_to_delete)
        elif s.lower().startswith('get '):
            name_to_get = s.split(' ')[1]
            return self.get_note_by_name(name_to_get)
        elif s== "good bye" or "close" or "exit":
           exit_handler()
           break
        elif s == "good bye" or "close" or "exit":
            exit_handler()
            break
        elif s:
            print('No command...')

if __name__ == "__main__":

    main()
