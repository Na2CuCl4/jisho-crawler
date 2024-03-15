# Merge n1_word, n2_word, ..., n5_word into jlpt_word.
# Author: Na2CuCl4
# Date: 2024/03/15


if __name__ == "__main__":
    # Read word list from file
    jlpt_list = set()
    for i in range(1, 6):
        with open(f"raw/n{i}_word.txt", "r") as file:
            word_list = file.read().split("\n")
        if word_list[-1] == "":
            word_list.pop()
        jlpt_list.update(set(word_list))

    # Sort word list
    jlpt_list = sorted(list(jlpt_list))

    # Save word list to file
    with open("raw/jlpt_word.txt", "w") as file:
        file.write("\n".join(jlpt_list) + "\n")
