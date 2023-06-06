def superset(set_1, set_2):
    if set_1 == set_2:
        return "Множества равны"
    elif set_1 > set_2:
        return f"Объект {set_1} является чистым супермножеством"
    elif set_1 < set_2:
        return f"Объект {set_2} является чистым супермножеством"
    else:
        return "Супермножеств не обнаружено"


def set_gen(array: list[int]) -> set[int]:
    i = 0
    while i < len(array):
        counter = array.count(array[i])
        if counter > 1:
            array[i] = str(array[i]) * counter
        i += 1
    return set(array)


def add_word(dictionary):
    try:
        eng_word = input("Введите английское слово: ")
        fra_word = input("Введите перевод на французский: ")
        dictionary[eng_word] = fra_word
        print("Слово успешно добавлено в словарь.")
    except Exception as e:
        print("Произошла ошибка при добавлении слова:", str(e))

def remove_word(dictionary):
    try:
        eng_word = input("Введите английское слово для удаления: ")
        del dictionary[eng_word]
        print("Слово успешно удалено из словаря.")
    except KeyError:
        print("Слово не найдено в словаре.")
    except Exception as e:
        print("Произошла ошибка при удалении слова:", str(e))

def search_word(dictionary):
    try:
        eng_word = input("Введите английское слово для поиска: ")
        if eng_word in dictionary:
            print("Перевод на французский:", dictionary[eng_word])
        else:
            print("Слово не найдено в словаре.")
    except Exception as e:
        print("Произошла ошибка при поиске слова:", str(e))

def replace_word(dictionary):
    try:
        eng_word = input("Введите английское слово для замены: ")
        if eng_word in dictionary:
            fra_word = input("Введите новый перевод на французский: ")
            dictionary[eng_word] = fra_word
            print("Слово успешно заменено.")
        else:
            print("Слово не найдено в словаре.")
    except Exception as e:
        print("Произошла ошибка при замене слова:", str(e))


def eng_french():
    dictionary = {}
    while True:
        print("\nМеню:\n1. Добавить слово\n2. Удалить слово\n3. Найти слово\n4. Заменить слово\n5. Выйти")
        choice = input("Выберите действие (1-5): ")
        match choice:
            case "1":
                add_word(dictionary)
            case "2":
                remove_word(dictionary)
            case "3":
                search_word(dictionary)
            case "4":
                replace_word(dictionary)
            case "5":
                break
            case _:
                print("Пожалуйста, выберите действие из списка.")


def main():
    print(superset({1, 5, 3, 6}, {3, 7}))
    print(superset({1, 5, 3, 6}, {6, 3, 1, 5}))

    print(set_gen([4, 4, 1, 2, 4]))
    print(set_gen([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]))

    print("\n\n=========СЛОВАРЬ=========\n\n")
    eng_french()

if __name__ == "__main__":
    main()
