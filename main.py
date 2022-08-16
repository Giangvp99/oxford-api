import requests
from bs4 import BeautifulSoup as soup
from http import cookiejar


class WordNotFound(Exception):
    """word not found in dictionary (404 status code)"""
    pass


class BlockAll(cookiejar.CookiePolicy):
    """policy to block cookies"""

    return_ok = (
        set_ok
    ) = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class Word(object):
    """retrive word info from oxford dictionary website"""

    definitions_selector = ".entry > ol .def"
    soup_data = None

    @classmethod
    def get_url(cls, word):
        """get url of word definition"""
        baseurl = "https://www.oxfordlearnersdictionaries.com/definition/english/"
        return baseurl + word

    @classmethod
    def delete(cls, selector):
        """ remove tag with specified selector in cls.soup_data """
        try:
            if selector == '[unbox="snippet"] ul li:last-child':
                for tag in cls.soup_data.select(selector):
                    if tag.text == "…":
                        tag.decompose()
            else:
                for tag in cls.soup_data.select(selector):
                    tag.decompose()
        except IndexError:
            pass

    @classmethod
    def get(cls, word):
        """get html soup of word"""
        req = requests.Session()
        req.cookies.set_policy(BlockAll())

        page_html = req.get(
            cls.get_url(word), timeout=5, headers={"User-agent": "mother animal"}
        )
        if page_html.status_code == 404:
            raise WordNotFound(word)
        else:
            cls.soup_data = soup(page_html.content, "html.parser")
        if cls.soup_data is not None:
            cls.delete('div#ring-links-box')
            cls.delete('div.symbols')
            cls.delete('span.jumplinks')
            cls.delete('[unbox="wordfinder"]')
            cls.delete('[unbox="extra_examples"]')
            cls.delete('[unbox="wordorigin"]')
            cls.delete('a.responsive_display_inline_on_smartphone')
            cls.delete('span.topic-g')
            cls.delete('[unbox="snippet"] ul li:last-child')
            cls.delete('span.dictlink-g')
            cls.delete('div.pron-link')
            cls.delete('[xt="see"]')
            cls.delete('[unbox="cult"]')
            cls.delete('#ox-enlarge')

    @classmethod
    def frontside(cls):
        """ Return: list of definitions """
        if cls.soup_data is None:
            return None
        res = ""
        for tag in cls.soup_data.select(cls.definitions_selector):
            res += str(tag)+"; "

        return res

    @classmethod
    def backside(cls):
        data = str(cls.soup_data.select("#entryContent")[0].prettify())
        data = data.replace('\r', '')
        data = data.replace('\t', '')
        data = data.replace('\n', '')
        return data

    @classmethod
    def to_anki(cls):
        front = cls.frontside()
        back = cls.backside()
        with open("res.txt", "a") as f:
            f.write(
                front+"\t"+"<!DOCTYPE html><html lang='en'><body>" + back+"</body>"+"</html>"+"\n")
            f.close()


try:
    with open("words.txt", "r") as f:
        words = f.readlines()

        for word in words:
            try:
                Word.get(word.strip())
                Word.to_anki()
            except WordNotFound as wnf:
                print(repr(wnf))
                continue
except:
    pass


# fix def
# colloc last item not '...'
