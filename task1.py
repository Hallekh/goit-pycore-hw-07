from collections import UserDict
from datetime import datetime, date

# Базовий клас для полів
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для зберігання імені контакту
class Name(Field):
    pass

# Клас для зберігання номера телефону з валідацією (10 цифр)
class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Номер телефону має складатися з 10 цифр.")
        super().__init__(value)

# Клас для зберігання дня народження; очікується формат DD.MM.YYYY
class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для запису контакту
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []       # Список об'єктів Phone
        self.birthday = None   # Об'єкт Birthday або None

    def add_phone(self, phone_str):
        phone_obj = Phone(phone_str)
        self.phones.append(phone_obj)

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)
        return f"День народження для {self.name.value} встановлено на {self.birthday.value.strftime('%d.%m.%Y')}."

    def days_to_birthday(self):
        if self.birthday is None:
            return None
        today = date.today()
        bday = self.birthday.value
        # Обчислюємо наступний день народження
        next_birthday = bday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = bday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = ", ".join(phone.value for phone in self.phones) if self.phones else "Немає телефонів"
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Немає даних"
        return f"Ім'я: {self.name.value} | Телефони: {phones_str} | День народження: {birthday_str}"

# Клас для адресної книги (наслідується від UserDict)
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower())

    def get_upcoming_birthdays(self, days=7):
        result = []
        today = date.today()
        for record in self.data.values():
            if record.birthday:
                next_bday = record.birthday.value.replace(year=today.year)
                if next_bday < today:
                    next_bday = record.birthday.value.replace(year=today.year + 1)
                delta = (next_bday - today).days
                if delta <= days:
                    result.append((record.name.value, delta))
        return result

# Допоміжна функція для розбору введеного рядка
def parse_input(user_input: str):
    tokens = user_input.strip().split()
    if not tokens:
        return "", []
    command = tokens[0].lower()
    args = tokens[1:]
    return command, args

# Основна функція CLI‑бота
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ("exit", "close"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            # Формат: add <ім'я> <телефон>
            if len(args) < 2:
                print("Введіть ім'я та номер телефону.")
                continue
            name, phone = args[0], args[1]
            record = book.find(name)
            if record is None:
                record = Record(name)
                book.add_record(record)
                message = "Контакт додано."
            else:
                message = "Контакт оновлено."
            try:
                record.add_phone(phone)
                print(message)
            except ValueError as ve:
                print(str(ve))
        elif command == "add-birthday":
            # Формат: add-birthday <ім'я> <дата народження у форматі DD.MM.YYYY>
            if len(args) < 2:
                print("Введіть ім'я та дату народження (DD.MM.YYYY).")
                continue
            name, birthday_str = args[0], args[1]
            record = book.find(name)
            if record is None:
                print("Контакт не знайдено.")
            else:
                try:
                    print(record.add_birthday(birthday_str))
                except ValueError as ve:
                    print(str(ve))
        elif command == "show-birthday":
            # Формат: show-birthday <ім'я>
            if len(args) < 1:
                print("Введіть ім'я контакту.")
                continue
            name = args[0]
            record = book.find(name)
            if record is None:
                print("Контакт не знайдено.")
            elif record.birthday:
                print(f"{record.name.value}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}")
            else:
                print("Дата народження не встановлена.")
        elif command == "birthdays":
            # Показує контакти, у яких день народження протягом наступних 7 днів
            upcoming = book.get_upcoming_birthdays(days=7)
            if not upcoming:
                print("Немає контактів з днем народження протягом наступного тижня.")
            else:
                for name, days_left in upcoming:
                    print(f"{name} через {days_left} днів")
        elif command == "all":
            if not book.data:
                print("Адресна книга порожня.")
            else:
                for record in book.data.values():
                    print(record)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
