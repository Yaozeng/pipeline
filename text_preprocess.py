import nltk
import re
import string
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer # or LancasterStemmer, RegexpStemmer, SnowballStemmer

default_stemmer = PorterStemmer()
default_stopwords = stopwords.words('english') # or any other list of your choice

def clean_text(text, stemming=False,stop_word=False,punctuation=False):

    def tokenize_text(text):
        return [w for s in sent_tokenize(text) for w in word_tokenize(s)]

    #标点和特殊符号
    def remove_special_characters(text, characters=string.punctuation.replace('-', '')):
        tokens = tokenize_text(text)
        pattern = re.compile('[{}]'.format(re.escape(characters)))
        return ' '.join(filter(None, [pattern.sub('', t) for t in tokens]))

    #词干化
    def stem_text(text, stemmer=default_stemmer):
        tokens = tokenize_text(text)
        return ' '.join([stemmer.stem(t) for t in tokens])

    #停用词
    def remove_stopwords(text, stop_words=default_stopwords):
        tokens = [w for w in tokenize_text(text) if w not in stop_words]
        return ' '.join(tokens)

    def normalize_whitespace(text, no_line_breaks=False):
        """
        Given ``text`` str, replace one or more spacings with a single space, and one
        or more line breaks with a single newline. Also strip leading/trailing whitespace.
        """
        LINEBREAK_REGEX = re.compile(r"((\r\n)|[\n\v])+")
        MULTI_WHITESPACE_TO_ONE_REGEX = re.compile(r"\s+")
        NONBREAKING_SPACE_REGEX = re.compile(r"(?!\n)\s+")

        if no_line_breaks:
            text = MULTI_WHITESPACE_TO_ONE_REGEX.sub(" ", text)
        else:
            text = NONBREAKING_SPACE_REGEX.sub(
                " ", LINEBREAK_REGEX.sub(r"\n", text)
            )
        return text.strip()

    text = text.lower()  # lowercase

    #remove url
    URL_REGEX = re.compile(
        r"(?:^|(?<![\w\/\.]))"
        # protocol identifier
        # r"(?:(?:https?|ftp)://)"  <-- alt?
        r"(?:(?:https?:\/\/|ftp:\/\/|www\d{0,3}\.))"
        # user:pass authentication
        r"(?:\S+(?::\S*)?@)?" r"(?:"
        # IP address exclusion
        # private & local networks
        r"(?!(?:10|127)(?:\.\d{1,3}){3})"
        r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        # IP address dotted notation octets
        # excludes loopback network 0.0.0.0
        # excludes reserved space >= 224.0.0.0
        # excludes network & broadcast addresses
        # (first & last IP address of each class)
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        r"|"
        # host name
        r"(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)"
        # domain name
        r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
        # TLD identifier
        r"(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))" r")"
        # port number
        r"(?::\d{2,5})?"
        # resource path
        r"(?:\/[^\)\]\}\s]*)?",
        # r"(?:$|(?![\w?!+&\/\)]))",
        # @jfilter: I removed the line above from the regex because I don't understand what it is used for, maybe it was useful?
        # But I made sure that it does not include ), ] and } in the URL.
        flags=re.UNICODE | re.IGNORECASE,
    )
    text=URL_REGEX.sub("<url>",text)

    #移除邮件
    EMAIL_REGEX = re.compile(
        r"(?:^|(?<=[^\w@.)]))([\w+-](\.(?!\.))?)*?[\w+-]@(?:\w-?)*?\w+(\.([a-z]{2,})){1,3}(?:$|(?=\b))",
        flags=re.IGNORECASE | re.UNICODE,
    )
    text=EMAIL_REGEX.sub("<email>",text)

    #移除电话号码
    PHONE_REGEX = re.compile(
        r"(?:^|(?<=[^\w)]))(\+?1[ .-]?)?(\(?\d{3}\)?[ .-]?)?(\d{3}[ .-]?\d{4})(\s?(?:ext\.?|[#x-])\s?\d{2,6})?(?:$|(?=\W))"
    )
    text=PHONE_REGEX.sub("<phone>",text)

    #remove numbers
    NUMBERS_REGEX = re.compile(
        r"(?:^|(?<=[^\w,.]))[+–-]?(([1-9]\d{0,2}(,\d{3})+(\.\d*)?)|([1-9]\d{0,2}([ .]\d{3})+(,\d*)?)|(\d*?[.,]\d+)|\d+)(?:$|(?=\b))"
    )
    text=NUMBERS_REGEX.sub("<number>",text)

    if stemming:
        text = stem_text(text)  # stemming
    if punctuation:
        text = remove_special_characters(text)  # remove punctuation and symbols
    if stop_word:
        text = remove_stopwords(text)  # remove stopwords

    text=normalize_whitespace(text) #whitespace

    return text

if __name__=="__main__":
    text="Hello, world!  Hello...\t \tworld?\n\nHello:\r\n\n\nWorld. I learned everything I know from www.stackoverflow.com and http://wikipedia.org/ and Mom."
    print(clean_text(text,punctuation=True))