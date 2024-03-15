# Crawl worddata from jisho.org.
# Author: Na2CuCl4
# Date: 2024/03/15


import json
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_word_data(word: str):
    """
    Get word data from jisho.org.
    :param word: word
    :return: word data
    """
    url = "https://jisho.org/word/" + quote(word)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get word readings
    reading_data = soup.find("div", class_="concept_light-representation")
    furigana_data = reading_data.find("span", class_="furigana")
    text_data = reading_data.find("span", class_="text")
    furigana = [furigana.text.strip() for furigana in furigana_data.contents if furigana != "\n"]
    text = [text.text.strip() for text in text_data.contents if text != "\n"]
    while len(furigana) != len(text):
        # Remove extra empty strings at the end of furigana
        if furigana[-1] == "":
            furigana.pop()

        # Split text into separate kanji
        if len(text) == 1 and len(text[0]) == len(furigana):
            text = list(text[0])

    # Get if the word is common
    common_data = soup.find("span", class_="concept_light-tag concept_light-common success label")
    common = True if common_data else False

    # Get JLPT level
    jlpt_data = soup.find_all("span", class_="concept_light-tag label")
    jlpt = 0
    for tag in jlpt_data:
        if "JLPT" in tag.text:
            jlpt = int(tag.text[-1])
            break

    # Get word meanings
    word_data = soup.find("div", class_="meanings-wrapper")
    tags_data = word_data.find_all("div", class_="meaning-tags")
    meanings_data = word_data.find_all("div", class_="meaning-wrapper")
    tags = [tag.text.strip() for tag in tags_data]
    meanings = []
    other_forms = ""
    notes = ""
    for tag, data in zip(tags, meanings_data):
        if tag == "Other forms":
            other_forms = data.find("span", class_="meaning-meaning").text.strip()
        elif tag == "Notes":
            notes = data.find("span").text.strip()
        else:
            meaning = data.find("span", class_="meaning-meaning").text.strip()
            supplement_data = data.find("span", class_="supplemental_info")
            supplement = supplement_data.text.strip() if supplement_data else ""
            sentence_data = data.find("div", class_="sentence")
            if sentence_data:
                sentence_jp = "".join([char.text.strip() for char in sentence_data.find_all("span", class_="unlinked")])
                sentence_jp_data = sentence_data.find("ul", class_="japanese japanese_gothic clearfix")
                for char in sentence_jp_data.contents:
                    if char.name is None:
                        sentence_jp += char.strip()
                sentence_en = sentence_data.find("span", class_="english").text.strip()
                sentence = sentence_jp + "\n" + sentence_en
            else:
                sentence = ""

            meanings.append({
                "tag": tag,
                "meaning": meaning,
                "supplement": supplement,
                "sentence": sentence
            })

    return {
        "word": word,
        "furigana": furigana,
        "text": text,
        "common": common,
        "jlpt": jlpt,
        "meanings": meanings,
        "other_forms": other_forms,
        "notes": notes
    }


if __name__ == "__main__":
    # Open word list
    with open("raw/n5_word.txt", "r") as file:
        word_list = file.read().split("\n")
    if word_list[-1] == "":
        word_list.pop()

    # Failed word list
    failed_word_list = []

    # Save word data to file
    with open("data/n5_word.json", "w", encoding="utf-8") as file:
        file.write("[\n")
        progress_bar = tqdm(word_list, desc="Processing words")
        for word in progress_bar:
            progress_bar.set_description(f"Word: {word}")

            try:
                word_data = get_word_data(word)
            except ConnectionResetError:
                print("Connection reset. Retrying...")
                word_data = get_word_data(word)
                continue
            except Exception as e:
                print(e)
                print("Word: " + word + " failed.")
                failed_word_list.append(word)

            file.write("  ")
            json.dump(word_data, file, ensure_ascii=False)
            file.write(",\n")

        file.seek(file.tell() - 2)
        file.write("\n]")

    # Write fail words into file
    with open("data/failed_word.txt", "w") as file:
        file.write("\n".join(failed_word_list))

    # Print results
    print(f"Crawling finished. {len(failed_word_list)} failed.")
