from imdb import IMDb, helpers
import re
import tvdbsimple as tvdb
from guessit import guessit
from Levenshtein import distance

tvdb.KEYS.API_KEY = '3ac0c4741aaf457d899b38da6ced68aa'


class Cache:
    """Show cache storage

    Attributes:
        show (dict): show dict
    """
    show = {}

    def caching(self, file_title, show_title, show_details):
        self.show.update({file_title: {"details": {}, "title": None}})
        self.show[file_title] = {"details": None, "title": None}
        show_details = {f"{episode['airedSeason']}{episode['airedEpisodeNumber']}": episode['episodeName'] for
                        episode in show_details}
        self.show[file_title]["details"] = show_details
        self.show[file_title]["title"] = show_title


class File:
    """Media file object

    Attributes:
        imdb: imdb object

    """
    imdb = None

    def __init__(self, name, ignore):
        self.file_infos = guessit(name)
        self.file_title = self.file_infos["title"]
        self.ignore = ignore

    def search_database(self, file_title, language):
        """Select into IMDb or TheTVDB the medias based on his title

        Args:
            media_type (str): Movie or ShowEpisode
            file_title (str): Media title
            language (str): Language for the search

        Raises:
            Exception: Generic exception

        Returns:
            dict: All the medias found
        """
        if self.__class__.__name__ == "Movie":
            self.imdb = IMDb()
            r = self.imdb.search_movie(file_title)
            return r
        else:
            o = tvdb.Search()
            r = o.series(file_title, language=language)
            return r

    def find_infos(self, all_results, title, max_depth=3):
        """Select into IMDb or TheTVDB only one media

        Args:
            all_results (dict): All results coming from IMDb or The TDVD
            title (str): Media title

        Raises:
            Exception: Generic exception

        Returns:
            dict: All infos regarding the media chosen
        """
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

    def get_details(self, id):
        if self.__class__.__name__ == "Movie":
            return self.imdb.get_movie(id)
        else:
            return tvdb.Series(id).Episodes.all()

    def error_or_ignore(self, data):
        if not data:
            if self.ignore:
                print(f"{self.__class__.__name__} not found and ignored '{self.file_title}'")
            else:
                raise Exception(f"{self.__class__.__name__} not found: {self.file_title}")


class Movie(File):
    """Movie object
    """

    def __init__(self, name, ignore, language, c=None):
        File.__init__(self, name, ignore)

        if "year" in self.file_title:
            self.file_title = f"{self.file_title} ({self.file_infos['year']})"

        # Search IDMB database with file name
        movies = self.search_database(self.file_title, language)
        self.error_or_ignore(movies)
        # Find the best match

        self.infos = self.find_infos(movies, "title")
        self.error_or_ignore(self.infos)
        # Get movie details
        movie_details = self.get_details(self.infos["movieID"])

        # f2 = helpers.getAKAsInLanguage(f, language)
        self.t = movie_details["title"]
        self.t = re.compile(r'(\([0-9]{4}\))').sub('', self.t).strip() if re.findall(r"([0-9]{4})",
                                                                                     self.t) else self.t
        self.x = self.file_infos['container']
        self.y = re.findall(r"([0-9]{4})", movie_details['original air date'])[0]


class ShowEpisode(File):
    """Show episode object
    """

    def __init__(self, name, ignore, language, c: Cache = None):
        File.__init__(self, name, ignore)
        if self.file_title not in c.show.keys():
            # Search TheTVDB database with file name
            shows = self.search_database(self.file_title, language)
            self.error_or_ignore(shows)
            # Find the best match
            self.infos = self.find_infos(shows, 'seriesName')
            self.error_or_ignore(self.infos)

            # Get show details
            show_details = self.get_details(self.infos['id'])
            # Caching the show
            c.caching(self.file_title, self.infos['seriesName'], show_details)
        self.s = str(self.file_infos['season'])
        self.s00 = self.s.rjust(2, '0')
        self.x = self.file_infos['container']

        # Handle multiple episode
        if isinstance(self.file_infos['episode'], list):
            self.e = '-'.join(str(e) for e in self.file_infos['episode'])
            self.e00 = '-'.join(str(e).rjust(2, '0') for e in self.file_infos['episode'])
            find_e = self.file_infos['episode'][0]
        else:
            self.e = str(self.file_infos['episode'])
            self.e00 = self.e.rjust(2, '0')
            find_e = self.e

        try:
            self.n = c.show[self.file_title]["title"].strip()
            self.t = c.show[self.file_title]["details"][f"{self.file_infos['season']}{find_e}"].strip()
        except Exception:
            raise Exception(f"Episode mismatch: {name}")
