import untangle
import urllib2
import inspect
import xml.etree.ElementTree as ET

def build_members_from_line(line):
    class_members = []
    in_quotes = False
    in_word = False
    word = ""
    for char in line[1:]:
        if char == " " and in_quotes is False:
            in_word = True
        elif char == "=" and in_quotes is False:
            class_members.append(word)
            word = ""
        elif char == '"' and in_quotes is False:
            in_quotes = True
        elif char == '"' and in_quotes is True:
            in_quotes = False
        elif in_quotes is True:
            pass
        elif in_word is True:
            word += char

    return class_members

def get_class_from_xml_link(link):
    data = urllib2.urlopen(link).read()
    classes_stack = []
    classes_dict = dict()

    for line in data.split('>'):
        if "<!--" not in line and len(line) > 0:
            if "</" not in line:
                class_name = line.split()[0][1:]
                for prev_class_name in classes_dict:
                    if class_name not in classes_dict[prev_class_name]:
                        classes_dict[prev_class_name].append(class_name)
                if not classes_dict.has_key(class_name):
                    class_members = []
                    class_members.extend(build_members_from_line(line))
                    classes_dict[class_name] = class_members
                    if line[-1] != "/":
                        classes_stack.append(class_name)

            else:#"</" in line
                class_name = line.split()[0][2:]
                if class_name in classes_stack[-1]:
                    classes_stack.pop(-1)

    return classes_dict

def build_init_func(members):
    init_func = ""
    for member in members:
        init_func += ", " + str(member) + "=None"
    init_func += "):\n"

    for member in members:
        init_func +="\t\tself." + str(member) + " = " + str(member) + "\n"

    return init_func

def build_setters_getters(members):
    set_get_txt = ""

    for member in members:
        set_get_txt += "\tdef set_" + str(member) + "(self, " + str(member) + "_val):\n"
        set_get_txt += "\t\tself." + str(member) + " = " + str(member) + "_val\n\n"
        set_get_txt += "\tdef get_" + str(member) + "(self):\n"
        set_get_txt += "\t\treturn self." + str(member) + "\n\n"
    return set_get_txt

def build_class(link):
    classes_with_members = get_class_from_xml_link(link)

    for class_name in classes_with_members:
        class_txt = ""
        class_txt += "class " + class_name + ":\n"
        class_txt += "\tdef __init__(self"
        class_txt += build_init_func(classes_with_members[class_name]) + "\n"
        class_txt += build_setters_getters(classes_with_members[class_name])

        f = open(class_name + ".txt", 'w')
        f.write(class_txt)



#link = "http://gd2.mlb.com/components/game/mlb/year_2015/month_07/day_09/gid_2015_07_09_tormlb_chamlb_1/inning/inning_5.xml"
link = "http://gd2.mlb.com/components/game/mlb/year_2015/month_07/day_01/gid_2015_07_01_bosmlb_tormlb_1/batters/434670.xml"

build_class(link)