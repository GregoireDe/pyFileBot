from imdb import IMDb, helpers
import re
import tvdbsimple as tvdb
from guessit import guessit
from Levenshtein import distance

tvdb.KEYS.API_KEY = '3ac0c4741aaf457d899b38da6ced68aa'


class Cache:
    show_list = {}
    show_title = {}

    def set_show(self, file_title, show_title, show_details):
        self.show_list[file_title] = {}
        show_details = {f"{episode['airedSeason']}{episode['airedEpisodeNumber']}": episode['episodeName'] for
                        episode in show_details}
        self.show_list[file_title].update(show_details)
        self.show_title = {file_title: show_title}


class File:
    title = None
    infos = None

    def __init__(self, name, ignore):
        self.file_infos = guessit(name)
        self.file_title = self.file_infos["title"]
        self.ignore = ignore

    def search_database(self, database_name, file_title, language):
        if database_name == "imdb":
            o = IMDb()
            r = o.search_movie(file_title)
            return o, r
        else:
            o = tvdb.Search()
            r = o.series(file_title, language=language)
            return r

    def find_infos(self, all_results, title, max_depth=3):
        if not all_results:
            raise Exception("Show/Movie not found")

        if len(all_results) == 1:
            return all_results[0]

        for k, v in list(enumerate(all_results))[:max_depth]:
            if self.file_title.lower() == all_results[k][title].lower():
                return all_results[k]
            elif distance(self.file_title, all_results[k][title]) < 1:
                return all_results[k]

        if not self.ignore:
            print(f"Multiple name found for '{self.file_title}'")
            for k, v in enumerate(all_results):
                print(f"{k}: {v[title]}")
            n = input("Enter the right one: ")
            return all_results[int(n)]
        return None

    def get_details(self, database_name, id, o=None):
        if database_name == "imdb":
            return o.get_movie(id)
        else:
            return tvdb.Series(id).Episodes.all()


class Movie(File):

    def __init__(self, name, ignore, language, c=None):
        File.__init__(self, name, ignore)

        if "year" in self.file_title:
            self.file_title = f"{self.file_title} ({self.file_infos['year']})"

        # Search IDMB database with file name
        o, movies = self.search_database("imdb", self.file_title, language)
        # Find the best match
        self.infos = self.find_infos(movies, "title")

        if not self.infos and ignore:
            return

        # Get movie details
        movie_details = self.get_details("imdb", self.infos.movieID, o)

        # f2 = helpers.getAKAsInLanguage(f, language)
        self.title = movie_details["title"]
        self.title = re.compile(r'(\([0-9]{4}\))').sub('', self.title).strip() if re.findall(r"([0-9]{4})",
                                                                                             self.title) else self.title
        self.ext = self.file_infos['container']
        self.year = re.findall(r"([0-9]{4})", movie_details['original air date'])[0]


class ShowEpisode(File):

    def __init__(self, name, ignore, language, c: Cache = None):
        File.__init__(self, name, ignore)
        if self.file_title not in c.show_list:

            # Search TheTVDB database with file name
            o, shows = self.search_database("tvdb", self.file_title, language)
            # Find the best match
            self.infos = self.find_infos(shows, 'seriesName')

            if not self.infos and ignore:
                return

            # Get show details
            show_details = self.get_details("tvdb", self.infos['id'])
            # Store in cache
            c.set_show(self.file_title, self.infos['seriesName'], show_details)

        self.season = self.file_infos['season']
        self.ext = self.file_infos['container']
        self.episode = self.file_infos['episode']
        try:
            self.show_title = c.show_title[self.file_title]
            self.title = c.show_list[self.file_title][f"{self.file_infos['season']}{self.file_infos['episode']}"]
        except Exception:
            raise Exception("Episode not found")
