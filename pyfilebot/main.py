from imdb import IMDb, helpers
import re
import tvdbsimple as tvdb
from guessit import guessit
from Levenshtein import distance

tvdb.KEYS.API_KEY = '3ac0c4741aaf457d899b38da6ced68aa'


class Cache:
    show_list = {}
    show_title = {}

    def set_show(self, file_title, show_title_imbd, episodes_detail):
        self.show_list[file_title] = {}
        show_details = {f"{episode['airedSeason']}{episode['airedEpisodeNumber']}": episode['episodeName'] for
                        episode in episodes_detail}
        self.show_list[file_title].update(show_details)
        self.show_title = {file_title: show_title_imbd}


class File:
    title = None
    infos = None

    def __init__(self, name, ignore):
        self.file_infos = guessit(name)
        self.file_title = self.file_infos["title"]
        self.ignore = ignore

    def find_infos(self, all_results, title, max_depth=3):
        if all_results:
            if len(all_results) == 1:
                return all_results[0]
            for k, v in list(enumerate(all_results))[:max_depth]:
                if self.file_title.lower() == all_results[k][title].lower():
                    return all_results[k]
                elif distance(self.file_title.lower(), all_results[k][title].lower()) < 3:
                    return all_results[k]
            if not self.ignore:
                print(f"Multiple name found for '{self.file_title}'")
                for k, v in enumerate(all_results):
                    print(f"{v[title]}: {k}")
                n = input("Enter the right one: ")
                return all_results[int(n)]
            return None
        else:
            raise Exception("Show/Movie not found")


class Movie(File):

    def __init__(self, name, ignore=False, language="En", c=None):
        File.__init__(self, name, ignore)
        o = IMDb()
        if "year" in self.file_title:
            self.file_title = f"{self.file_title} {self.file_infos['year']}"
        results = o.search_movie(self.file_title)
        self.infos = self.find_infos(results, "title")
        if not self.infos and ignore:
            return
        m = o.get_movie(self.infos.movieID)
        self.infos.update(m)
        # f2 = helpers.getAKAsInLanguage(f, language)
        if re.findall(r"([0-9]{4})", self.infos["title"]):
            self.infos["title"] = re.compile(r'(\([0-9]{4}\))').sub('', self.infos["title"]).strip()
        self.ext = self.file_infos['container']
        self.title = self.infos["title"]
        self.year = re.findall(r"([0-9]{4})", self.infos['original air date'])[0]


class ShowEpisode(File):

    def __init__(self, name, ignore=False, language="EN", c: Cache = None):
        File.__init__(self, name, ignore)
        if self.file_title not in c.show_list:
            search = tvdb.Search()
            results = search.series(self.file_title, language=language)
            self.infos = self.find_infos(results, 'seriesName')
            if not ignore:
                episodes_detail = tvdb.Series(self.infos['id']).Episodes.all()
                c.set_show(self.file_title, self.infos['seriesName'], episodes_detail)
        self.season = self.file_infos['season']
        self.ext = self.file_infos['container']
        self.episode = self.file_infos['episode']
        try:
            self.show_title = c.show_title[self.file_title]
            self.title = c.show_list[self.file_title][f"{self.file_infos['season']}{self.file_infos['episode']}"]
        except Exception:
            raise Exception("Episode not found")
