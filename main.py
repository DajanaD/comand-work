from collections import UserDict
import datetime
import json
import cmd
import sys


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
                def formatted_numbers():          # форма для пошуку телефона
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
    # загальна форма
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
    
book = AddressBook()
