import pymorphy2

def _is_functional_part_of_speech(part_of_speech):
    if part_of_speech == 'PREP' or part_of_speech == 'CONJ' or part_of_speech == 'PRCL' or part_of_speech == 'INTJ':
        return True


def stem_text(request_text):
    """
    Стемироание - приведение слова к его изначальной форме. Например, слова "покупка" и "купить" будет приведены
    к слову "купить". Это очень полезно для оценки конкуренции по вхождению ключевых слов в заголовок страницы.
    Метод _is_functional_part_of_speech отсекает служебные части речи. Они не нужны.
    """
    morpher = pymorphy2.MorphAnalyzer()
    stemmed_text = []
    for word in request_text.split():
        stemed_word = morpher.parse(word)
        the_best_form_of_stemed_word = stemed_word[0]
        part_of_speech = str(the_best_form_of_stemed_word.tag.POS)
        if not _is_functional_part_of_speech(part_of_speech):
            stemmed_text.append(the_best_form_of_stemed_word.normal_form)

    return stemmed_text
#    logger.info(f'Стемированный запрос: {self.stemmed_request}')