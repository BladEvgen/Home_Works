import re


def domain_from_email(emails: list[str]) -> list[str]:
    domains = []
    for email in emails:
        domains.append(email.split("@")[-1])
    return domains


def start_from_vowel_letter(text: str) -> list[str]:
    pattern = r"\b[aeiouAEIOU][A-Za-z0-9_]*\b"
    vowel_words = re.findall(pattern, text)
    return vowel_words


def multiple_delimiters(text: str) -> list[str]:
    return re.split(";|,|\?|\!|\n|\.", text)


def elections(votes: list[str]):
    candidates = {
        "Аскаров": 0,
        "Бекмуханов": 0,
        "Ернур": 0,
        "Пешая": 0,
        "Карим": 0,
        "Шаримазданов": 0,
    }
    for vote in votes:
        if vote in candidates:
            candidates[vote] += 1
    max_votes = max(candidates.values())
    
    winners = [candidate  for candidate , vote in candidates.items() if votes == max_votes]
    
    return winners

def main():
    print("\n\n=========Домены с почт=========\n\n")
    email_list = [
        "myl1988@band-freier.de",
        "lafoole1@gmailvn.net",
        "m2010zh@turtlegrassllc.com",
    ]
    print(f"Лист доменов: {domain_from_email(email_list)}")
    print("\n\n=========Слова с гласной буквы=========\n\n")
    print(f'{start_from_vowel_letter(input("введите текст на английском языке: "))}')
    print("\n\n=========Разбитие строки по нескольким разделителям=========\n\n")
    print(multiple_delimiters("Hello, world! How are you? I am fine."))
    votes = ['Ернур']
    winner = elections(votes=votes)
    print(winner)
if __name__ == "__main__":
    main()
