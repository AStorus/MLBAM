from UrlCreator import UrlCreator
import xml.etree.ElementTree as ET
import httplib2
import pdb
import re

class Search:

    urlcreator = UrlCreator()
    http = httplib2.Http()
    #for directory 'day', valid xml files would be whats in the list
    xml_files_in_dir = {
        "day": ["master_scoreboard.xml", "playertracker.xml", "scoreboard.xml"],
        "pitchers" : [re.compile(r'^\d{6}_\d{1}.xml'), re.compile(r'^\d{6}.xml')],
        "batters" : [re.compile(r'^\d{6}_\d{1}.xml'), re.compile(r'^\d{6}.xml')],
        "pitching" : [re.compile(r'^[a-z]{3}_\d{1}.xml')],
        "inning" : [re.compile(r'inning_')],
        "onbase" : ["linescore.xml", "plays.xml"],
        "gid" : ["players.xml", "bench.xml", "boxscore.xml", "eventlog.xml", "game_events.xml", "linescore.xml"]
    }

    def __init__(self):
        pass

    def search_dir(self, base_url=urlcreator.base_url):
        #returns set of all subdirectories of current url
        child_dir_urls = self.urlcreator.get_subdirectories(base_url)
        child_dir_urls_with_term = set()
        #recursively call this function on all found sub directories
        for child_dir_url in child_dir_urls:
            child_dir_urls_with_term = child_dir_urls_with_term.union(self.search_dir(base_url + child_dir_url))

        lowest_dir_name = self.urlcreator.get_lowest_dir_name(base_url)
        #list of all xml file names / patterns which are valid for a given directory
        xml_links_on_page = self.xml_files_in_dir.get(lowest_dir_name)

        #returns set of all files which match name/pattern above
        if xml_links_on_page is None:
            xml_links_with_term = self.urlcreator.get_xml_on_page(base_url)
        else:
            xml_links_with_term = self.urlcreator.get_xml_on_page(base_url, set(xml_links_on_page))

        #returns both subdirectories and filenames
        ret_val = child_dir_urls_with_term.union(xml_links_with_term)
        return ret_val

    def search_xml_in_dir(self, dir_url, *search_terms):
        #get all xml links on page
        xml_links = self.urlcreator.get_xml_on_page(dir_url)
        #key is url, data is the parsed xml file
        xml = dict()
        for link in xml_links:
            status, raw_page = self.http.request(dir_url + link)
            for keyword in search_terms:
                if keyword in raw_page:
                    xml[dir_url + link] = ET.fromstring(raw_page)

        return xml


search = Search()
url = "http://gd2.mlb.com/components/game/mlb/year_2012/month_08/day_14/gid_2012_08_14_tbamlb_seamlb_1/"

xml_links = search.search_dir(url)
for xml_link in xml_links:
    print xml_link