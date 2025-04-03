from collections import UserDict
from datetime import datetime, date

class Field:
    """Базовий клас для полів запису."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """Клас для зберігання імені контакту."""
    pass

class Phone(Field):
    """Клас для зберігання номера телефону з валідацією (10 цифр)."""
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Номер телефону має складатися з 10 цифр.")
        super().__init__(value)

class Birthday(Field):
    """Клас для зберігання дня народження. Очікується формат 'DD.MM.YYYY'."""
    def __init__(self, value):
        try:
            # Перетворюємо рядок у об'єкт date
            birthday_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    """Клас для зберігання інформації про контакт:
    ім'я, список телефонів та день народження (опціонально).
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []   # Список об'єктів Phone
        self.birthday = None  # Об'єкт Birthday або None

    def add_phone(self, phone_str):
        """Додає номер телефону до запису."""
        phone_obj = Phone(phone_str)
        self.phones.append(phone_obj)

    def remove_phone(self, phone_str):
        """Видаляє номер телефону з запису."""
        for phone in self.phones:
            if phone.value == phone_str:
                self.phones.remove(phone)
                return f"Телефон {phone_str} видалено."
        return "Телефон не знайдено."

    def edit_phone(self, old_phone, new_phone):
        """Редагує номер телефону: замінює old_phone на new_phone."""
        for phone in self.phones:
            if phone.value == old_phone:
                new_phone_obj = Phone(new_phone)  # валідація нового номера
                phone.value = new_phone_obj.value
                return f"Телефон {old_phone} змінено на {new_phone}."
        return "Телефон не знайдено."

    def find_phone(self, phone_str):
        """Пошук номера телефону в записі."""
        for phone in self.phones:
            if phone.value == phone_str:
                return phone.value
        return "Телефон не знайдено."

    def add_birthday(self, birthday_str):
        """Додає день народження до контакту.
           Формат: DD.MM.YYYY
        """
        self.birthday = Birthday(birthday_str)
        return f"День народження {self.birthday.value.strftime('%d.%m.%Y')} додано."

    def days_to_birthday(self):
        """Обчислює кількість днів до наступного дня народження.
           Якщо день народження не встановлено, повертає None.
        """
        if self.birthday is None:
            return None
        today = date.today()
        bday = self.birthday.value
        # Створюємо дату наступного дня народження з поточного року
        next_birthday = bday.replace(year=today.year)
        if next_birthday < today:
            next_birthday = bday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = '; '.join(phone.value for phone in self.phones) if self.phones else "Немає телефонів"
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Немає даних"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    """Клас для зберігання та управління записами адресної книги."""
    def add_record(self, record):
        """Додає запис до адресної книги. Ключ – ім'я контакту у нижньому регістрі."""
        self.data[record.name.value.lower()] = record

    def find(self, name):
        """Знаходить запис за ім'ям (пошук нечутливий до регістру)."""
        return self.data.get(name.lower(), "Запис не знайдено.")

    def delete(self, name):
        """Видаляє запис за ім'ям (пошук нечутливий до регістру)."""
        if name.lower() in self.data:
            del self.data[name.lower()]
            return f"Запис {name} видалено."
        return "Запис не знайдено."

    def get_upcoming_birthdays(self, days=7):
        """Повертає список контактів, у яких день народження настане протягом наступних 'days' днів.
           За замовчуванням шукаємо для наступних 7 днів.
        """
        upcoming = []
        today = date.today()
        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value
                next_birthday = bday.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = bday.replace(year=today.year + 1)
                delta = (next_birthday - today).days
                if 0 <= delta <= days:
                    upcoming.append(record)
        return upcoming

if __name__ == "__main__":
    
    book = AddressBook()

    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    print(john_record.add_birthday("09.04.1990"))  # додаємо день народження
    book.add_record(john_record)

    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    print(jane_record.add_birthday("11.04.1995"))
    book.add_record(jane_record)

    print("Всі записи:")
    for record in book.data.values():
        print(record)

    # Отримання контактів з днем народження протягом наступного тижня
    print("\nКонтакти з днем народження протягом наступного тижня:")
    upcoming = book.get_upcoming_birthdays(days=7)
    for record in upcoming:
        days_left = record.days_to_birthday()
        print(f"{record.name.value} (через {days_left} днів)")
