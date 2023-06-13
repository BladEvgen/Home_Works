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


def elections(candidate_list: list[str]):
    vote_counts = {}
    for candidate in candidate_list:
        if candidate in vote_counts:
            vote_counts[candidate] += 1
        else:
            vote_counts[candidate] = 1
    max_votes = max(vote_counts.values())
    winners = [
        candidate for candidate, votes in vote_counts.items() if votes == max_votes
    ]
    if len(winners) == 1:
        winner = winners[0]
        num_votes = max_votes
    else:
        # Multiple winners, sort by the length of their names and choose the winner with the minimum number of letters
        sorted_winners = sorted(winners, key=len)
        winner = sorted_winners[0]
        num_votes = max_votes

    return winner, num_votes


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

    candidates = [
        "Askarov",
        "Bekmukhanov",
        "Yernur",
        "Peshaya",
        "Karim",
        "Sharimazdanov",
    ]
    voter_choice = "Yernur"


if __name__ == "__main__":
    main()
