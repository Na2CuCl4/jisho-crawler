# Crawl word list from jisho.org.
# Author: Na2CuCl4
# Date: 2024/03/15


from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup


def get_word_list(tag: list):
    """
    Get word list from jisho.org.
    :param tag: list of tags
    :return: href list of words
    """
    if 'word' not in tag:
        tag.append('word')

    base_url = "https://jisho.org/search/" + "%20".join(["%23" + word for word in tag])
    filename = f"raw/{'_'.join(tag)}.txt"
    page_num = 1

    with open(filename, "w") as file:
        while True:
            try:
                response = requests.get(base_url + "?page=" + str(page_num))
                soup = BeautifulSoup(response.text, "html.parser")
                word_list = soup.find_all("a", class_="light-details_link")
                if len(word_list) == 0:
                    break

                href_list = [unquote(word["href"][17:]) for word in word_list]
                file.write("\n".join(href_list) + "\n")
                print("Page " + str(page_num) + " done.")
                page_num += 1
            except Exception as e:
                print(e)
                print("Page " + str(page_num) + " failed, retrying.")


if __name__ == "__main__":
    # Save word list to file
    tag_list = [["common"]]

    for tag in tag_list:
        print("Tag " + tag[0] + " start.")
        get_word_list(tag)
        print("Tag " + tag[0] + " done.")
