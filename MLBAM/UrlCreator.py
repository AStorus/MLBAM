import httplib2
from datetime import datetime
from BeautifulSoup import BeautifulSoup, SoupStrainer
import pdb
import re

class UrlCreator:

    base_url = "http://gd2.mlb.com/components/game/mlb/"
    http = httplib2.Http()
    parent_dir = {
        "mlb": ["year_"],
        "year_": ["month_"],
        "month_": ["day_"],
        "day_": ["batters/", "pitchers/", "pitching_staff/", "gid_"],
        "gid_": ["batters/", "inning/", "onbase/", "pitchers/"]
    }

    def MLBCrawler(self):
        pass

    def get_hrefs_on_page(self, response):
        hrefs = set()
        for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
            hrefs.add(link.get('href'))
        return hrefs

    def filter_hrefs_keyword_only(self, hrefs_set, curr_dir, keywords=set()):
        relevant_hrefs = set()
        for href in hrefs_set:
            is_href_wanted = False
            for keyword in keywords:
                if keyword in href:
                    is_href_wanted = True
            if is_href_wanted:
                relevant_hrefs.add(href)

            if self.is_incorrect_date_href(href):
                relevant_hrefs.add("/" + curr_dir + "/" + href)
        return relevant_hrefs

    def is_incorrect_date_href(self, href):
        curr_year = datetime.now().year
        if "year_" in href and ".xml" not in href:
            data_year = href[href.index("year_") + len("year_") : href.index("/",href.index("year_"))]
            if data_year.isdigit() is False:
                return False
            elif int(data_year) > curr_year or int(data_year) < 2005:#2005 first year data was collected
                return False

            curr_month = datetime.now().month
            if "month_" in href and ".xml" not in href:
                data_month = int(href[href.index("month_") + len("month_") : href.index("/",href.index("month_"))])
                if data_month > curr_month:
                    return False

                curr_day = datetime.now().day
                if "day_" in href and ".xml" not in href:
                    data_day = int(href[href.index("day_") + len("day_") : href.index("/",href.index("day_"))])
                    if data_day > curr_day:
                        return False
        return True

    def get_lowest_dir_name(self, url):
        rightmost_slash = url.rfind("/")
        second_rightmost_slash = url[:-1].rfind("/") + 1
        underscore = url.find("_", second_rightmost_slash, rightmost_slash)
        if underscore != -1:
            lowest_dir_name = url[second_rightmost_slash:min(underscore, rightmost_slash)]
        else:
            lowest_dir_name = url[second_rightmost_slash: rightmost_slash]
        return lowest_dir_name

    def get_subdirectories(self, url=base_url):
        status, response = self.http.request(url)
        #TODO: if status code is 400, do soemthing ...
        hrefs = self.get_hrefs_on_page(response)
        #lowest directory name
        curr_dir = url[url[:-1].rfind("/") + 1:url.rfind("/")]
        #valid child dirs represent what subdirectories to search given a current directory
        valid_child_dirs = []
        for elem in self.parent_dir:
            if elem in curr_dir:
                valid_child_dirs = self.parent_dir[elem][:]

        #filter out invalid subdirectories
        filtered_hrefs = set()
        for href in hrefs:
            filtered_hrefs = filtered_hrefs.union(self.filter_hrefs_keyword_only(hrefs, curr_dir, valid_child_dirs))
        return filtered_hrefs

    def get_xml_on_page(self, url, filenames=set()):
        status, response = self.http.request(url)
        xml_hrefs = set()
        for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
            link_name = link.get('href')
            if ".xml" in link_name:
                #for each keyword, add hrefs that match filenames
                for filename in filenames:
                    if type(filename) == str:
                        if filename in link_name:
                            xml_hrefs.add(url + link_name)
                    elif type(filename) != str:
                        if filename.match(link_name) is not None:
                            xml_hrefs.add(url + link_name)
        return xml_hrefs

urlcreator = UrlCreator()




