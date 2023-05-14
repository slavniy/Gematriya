from analyzer_func import create_report
from base_genogram_func import word_numerical_value
from e_f_fl_calculate import e
import webbrowser
text = open('data.txt').read()
# checker
select_word = False
select_sentence = False
select_paragraf = False
select_area = False


def get_areas(text):
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    spechial_words = ['#Область', '#Глава', '\n\n']
    for separator in spechial_words:
        text = text.replace(separator, '<br>')
    return text.split('<br>')


def get_paragraphs(text):
    return text.split('\n')


def get_sentences(text):
    separators = ['.', '!', '?']
    for separator in separators:
        text = text.replace(separator, separator + '<br>')
    return text.split('<br>')


def get_words(text):
    prepared_text = ''
    for letter in text:
        if (letter.isalpha() or letter.isdigit() or letter == ' '):
            prepared_text += letter
    return prepared_text.split()


areas = get_areas(text)
paragraphs = [get_paragraphs(area) for area in areas]
sentences = []
for area in paragraphs:
    sentences.append([get_sentences(paragraph) for paragraph in area])

tree = get_areas(text)
for area_number in range(len(tree)):
    tree[area_number] = get_paragraphs(tree[area_number])
    for paragraph_number in range(len(tree[area_number])):
        tree[area_number][paragraph_number] = get_sentences(tree[area_number][paragraph_number])
        for sentence_number in range(len(tree[area_number][paragraph_number])):
            tree[area_number][paragraph_number][sentence_number] = get_words(
                tree[area_number][paragraph_number][sentence_number])
words = tree

'''Получение адресов слов'''
statistics = dict()
for area_number in range(len(tree)):
    for paragraph_number in range(len(tree[area_number])):
        for sentence_number in range(len(tree[area_number][paragraph_number])):
            for word_number in range(len(tree[area_number][paragraph_number][sentence_number])):
                address = f'{area_number+1}:{paragraph_number+1}:{sentence_number+1}:{word_number+1}'
                word = tree[area_number][paragraph_number][sentence_number][word_number]
                if word not in statistics:
                    statistics[word] = {'addresses':[], 'text':word, 'n_v': word_numerical_value(word),'energy': e(word), 'length':len(word), 'count':0}
                statistics[word]['count'] += 1
                statistics[word]['addresses'].append(address)
data = list(statistics.values())
print(data)
path = create_report('text_analyze_report.html', data=data)
webbrowser.open(path)
