import  re
from database import MongoBase
from settings import settings

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs

    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]

class WordTokenizer(object):
    '''
        WordTokenizer divides each string into isolated
        words, this operation is performed using python
        Regular Expression
    '''

    def __init__(self):
        self.tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
        self.emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
        self.undef_re = re.compile(r'^'+regex_str[-1]+'$', re.VERBOSE | re.IGNORECASE)
        self.url_re = re.compile(r'('+'|'.join([regex_str[1], regex_str[4]])+')',
                                 re.VERBOSE | re.IGNORECASE)

    def tokenize(self, word):
        return self.tokens_re.findall(word)

    def preprocess(self, s, lowercase=False, words_only=False):
        tokens = self.tokenize(s)
        if words_only:
            tokens = [token
                      for token in tokens
                      if not self.emoticon_re.search(token)
                      and not self.url_re.search(token)
                      and not self.undef_re.search(token)
                      ]
        ## Lowercase option for words, not emoticon
        if lowercase:
            tokens = [token if self.emoticon_re.search(token) else token.lower() for token in tokens]
        return tokens

class WordStats(object):

    def __init__(self):
        pass

def get_string_list( basename ):
    mn = MongoBase(settings['db_addr'])
    db_cur = mn.get_dataset( basename )
    return db_cur


def main():
    tweet = "RT @marcobonzanini: just an example! :D http://example.com #NLP"
    db_cur = get_string_list('location')
    ws = WordTokenizer()
    print ws.preprocess(tweet, lowercase=True, words_only=True)


if __name__ == '__main__':
    main()