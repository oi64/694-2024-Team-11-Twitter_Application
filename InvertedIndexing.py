##
import re
import string
from nltk.stem import PorterStemmer

##
# Create a Porter stemmer object

str = "Editor at john.doe@example.com http://www.smashingmagazine.com https://t.co/Qelcm8VxFo by night. Editor, photographer, fan of good coffee and bicycles by day. 10.4 :)"

##
url_pattern = r'^http'
url_pattern_with_TLD = r'https?://(?:www\.)?([a-zA-Z0-9.-]+)\.\w+$'
punctuation_pattern = r'^[' + re.escape(string.punctuation) + r']+$'
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
porter = PorterStemmer()

def filter_tokens(str):
    filtered_tokens = []
    for token in str.split():
        if re.match(email_pattern, token):
            continue
        if re.match(punctuation_pattern, token):
            continue
        if re.match(url_pattern, token):
            match = re.match(url_pattern_with_TLD, token)
            if match:
                filtered_tokens.append(match.group(1).lower())
            else:
                continue
        else:
            filtered_tokens.append(porter.stem(re.sub(r'(?<!\d)\.(?!\d)|[^\w\s.]', '', token).lower()))

    return filtered_tokens


print(filter_tokens(str))

##
from nltk.stem import SnowballStemmer

snowball = SnowballStemmer(language='english')
word = 'coffee'
stemmed_word = snowball.stem(word)
print(stemmed_word)

##
