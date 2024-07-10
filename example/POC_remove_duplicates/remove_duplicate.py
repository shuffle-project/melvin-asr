def remove_duplicates(text1, text2):
    # Zerlege die Texte in Wörterlisten
    words1 = text1.split()
    words2 = text2.split()

    # Nimm die letzten 5 Wörter von text1 und die ersten 5 Wörter von text2
    last_five_words_text1 = words1[-5:]
    first_five_words_text2 = words2[:5]

    # Erstelle eine Liste der Wörter in text2 ohne die Duplikate
    new_words2 = first_five_words_text2.copy()
    for word in first_five_words_text2:
        if word in last_five_words_text1:
            new_words2.remove(word)

    # Kombiniere die neuen Wörter von text2 mit dem Rest der Wörter von text2
    unique_text2 = new_words2 + words2[5:]

    # Erstelle den neuen Text2 String
    return " ".join(unique_text2)


# Beispieltexte
text1 = "Ich rufe nun auf den Tagesordnungspunkt. Punkt 2. Abgabe einer Regierungserklärung durch den Bundeskanzler zum Europäischen"
text2 = "Europäischen Rat am 21. und 22. März 2024."

# Entferne Duplikate
result_text2 = remove_duplicates(text1, text2)
print(result_text2)
