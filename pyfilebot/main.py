import re
import os

import tvdbsimple as tvdb
import pycountry
from imdb import IMDb, helpers, linguistics, Movie as imdbMovie
from guessit import guessit
from Levenshtein import distance


tvdb.KEYS.API_KEY = '3ac0c4741aaf457d899b38da6ced68aa'


class Cache:
    """Show cache storage

    Attributes:
        show (dict): show dict
    """
    show = {}

    def caching(self, file_title: str, show_title: str, show_details: dict):
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

    def __init__(self, file_path: str, ignore: bool):
        self.name = os.path.basename(file_path)
        self.file_infos = guessit(self.name )
        self.file_title = self.file_infos["title"]
        if "year" in self.file_infos:
            self.file_title = f'{self.file_infos["title"]} ({self.file_infos["year"]})'
        self.ignore = ignore

    def search_database(self, file_title: str, language: str):
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

    def find_infos(self, medias: dict, title: str, max_depth: int = 3):
        """Select into IMDb or TheTVDB only one media

        Args:
            medias (dict): All results coming from IMDb or The TDVD
            title (str): Media title
            max_depth (int): Maximum depth to lookup for strict match / Levenstein distance

        Raises:
            Exception: Generic exception

        Returns:
            dict: All infos regarding the media chosen
        """
        if len(medias) == 1:
            return medias[0]

        for k, v in list(enumerate(medias))[:max_depth]:
            if self.file_title.lower() == medias[k][title].lower():
                return medias[k]
            elif distance(self.file_title, medias[k][title]) < 1:
                return medias[k]

        if not self.ignore:
            print(f"Multiple name found for '{self.file_title}'")
            # No need for more than 6 medias match
            medias = medias[:6]
            for k, v in enumerate(medias):
                print(f"{k}: {v[title]}")
            n = input("Enter the right one: ")
            return medias[int(n)]
        return None

    def get_details(self, id: str):
        """Get all details from IMDb or TheTVDB media ID

       Args:
           id (str): A media ID

       Returns:
           dict: All infos regarding the media
       """
        if self.__class__.__name__ == "Movie":
            return self.imdb.get_movie(id, ['main', 'akas'])
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

    def __init__(self, file_path: str, ignore: bool, language: str, c=None):
        File.__init__(self, file_path, ignore)

        # Search IDMB database with file name
        movies = self.search_database(self.file_title, language)
        self.error_or_ignore(movies)
        # Find the best match

        self.infos = self.find_infos(movies, "title").__dict__
        self.error_or_ignore(self.infos)
        # Get movie details
        movie_details = self.get_details(self.infos["movieID"])

        self.n = self._get_language_title(movie_details, language)

        self.n = re.compile(r"(\([0-9]{4}\))").sub('', self.n).strip() if re.findall(r"([0-9]{4})", self.n) else self.n
        self.x = self.file_infos['container']
        self.y = re.findall(r"([0-9]{4})", movie_details['original air date'])[0]

    @staticmethod
    def _get_language_title(movie: imdbMovie, language: str):
        """Get language title for a movie (IMDBpy getAKAsInLanguage() is not working at all)

        Args:
            movie (object): Movie object
            language (str): Language wanted

        Returns:
            str: Movie title
        """
        language = language.lower()
        f2 = helpers.akasLanguages(movie)
        title = {}
        for f in f2:
            f_l = re.findall(r'\w+$|\w+(?=\s\()', f[1])
            if f_l:
                l = linguistics.COUNTRY_LANG.get(f_l[0])
                pylang_name = pycountry.languages.get(name=l)
                if pylang_name:
                    title.update({pylang_name.alpha_2: re.findall(r'.*(?=\s\w+\s\()|.*(?=\s\w+)', f[1])[0]})
        if language in title.keys():
            return title[language]
        return movie


class ShowEpisode(File):
    """Show episode object
    """

    def __init__(self, file_path: str, ignore: bool, language: str, c: Cache = None):
        File.__init__(self, file_path, ignore)
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
