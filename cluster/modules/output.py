from columnar import columnar
from click import style
from packaging import version
import os, re, time, requests, json, ast, datetime, csv
#from .logging import Logger

class Output:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    MARKER = u"\u2309\u169B\u22B8"
    # u'\u2717' means values is None or not defined
    # u'\u2714' means value is defined

    global patterns, _logger
    
    patterns = [(u'\u2714', lambda text: style(text, fg='green')), \
                ('True', lambda text: style(text, fg='green')), \
                ('False', lambda text: style(text, fg='yellow'))]

    def time_taken(start_time):
        print(Output.GREEN + "\nTotal time taken: " + Output.RESET + \
        "{}s".format(round((time.time() - start_time), 2)))

    # prints separator line between output
    def separator(color, char, l):
        if l: return
        columns, rows = os.get_terminal_size(0)
        for i in range(columns):
            print (color + char, end="" + Output.RESET)
        print ("\n")

    # sorts data by given field
    def sort_data(data, field):
        try:
            if field:
                data.sort(key=lambda x: x[int(field)])
            else:
                data.sort(key=lambda x: x[0])
        except AttributeError:
            print("Empty data received!")
            exit()
        return data

    def summary(data_len, object_type):
        print(Output.PURPLE + "\nTotal {} count: ".format(object_type) + Output.RESET + str(data_len))

    # prints table from lists of lists: data
    def print_table(data, headers):
        try:
            if len(data) != 0:
                headers = headers[:6]
                table = columnar(data, headers, no_borders=True, row_sep='-')
                print (table)
                #print("Total: {}".format(len(data)))
        except:
            print("Empty/Incorrect data received!")
            exit()

    # prints data in tree format from lists data and headers
    def print_tree(data, headers):
        h = sorted(headers[1:], key=len)    # sorting to find longest element in headers for :
        for d in data:
            heading = headers[0] + ": "
            Output.separator(Output.YELLOW, '.' , '')
            print(Output.BOLD + heading + d[0] + Output.RESET)

            # printing the tree
            for i in range(len(headers)):
                try:
                    #https://www.compart.com/en/unicode/mirrored
                    # printing 2nd level tree in if condition
                    if not '\n' in d[i+1]:
                        print("".ljust(len(heading)) + Output.MARKER + headers[i+1].ljust(len(h[-1])) + ": " + str(d[i+1]))
                    else:
                        i_padding = "".ljust(len(heading)) + Output.MARKER + headers[i+1] + ": "
                        print(i_padding)

                        # printing 3rd level tree in else condition
                        for x in d[i+1].split("\n"):
                            # print("".ljust(len(i_padding)) + Output.MARKER + str(x))
                            if '[' in x:
                                x = ast.literal_eval(x)

                                # printing 4th level tree in else condition                          
                                for j in x:
                                    y_padding = len(i_padding + Output.MARKER + previous)
                                    if y_padding > 50: y_padding = 50
                                    print("".ljust(y_padding) + Output.MARKER + j)
                            else:
                                print("".ljust(len(i_padding)) + Output.MARKER + x)
                                previous = x

                    # print("".ljust(len(heading)) + Output.MARKER + headers[i+1].ljust(len(h[-1])) + ": " + str(d[i+1]))
                except:
                    pass
        #print("Total: {}".format(len(data)))

    # prints data in json format from lists data and headers
    def print_json(data, headers):
        json_data = []
        headers = [x.lower() for x in headers]
        for item in data:
            temp_dic = {}
            # storing json data in dict for each list in data
            for i in range(len(headers)):
                for j in range(len(item)):
                    if not '\n' in str(item[i]):
                        temp_dic.update({headers[i]: item[i]})
                    else:
                        item[i].split("\n")
                        temp_dic.update({headers[i]: item[i].split("\n")})

            # appending all json dicts to form a list
            json_data.append(temp_dic)
     
        print(json.dumps(json_data))

        directory = './reports/json/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # writing out json data in file based on object type and config being checked
        filename = directory + headers[0] + str(time.time()) + '_report.json'
        f = open(filename, 'w')
        f.write(json.dumps(json_data))
        f.close()       
        return json.dumps(json_data)

    def csv_out(data, headers):
        directory = './reports/csv/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = directory + headers[0] + str(time.time()) + '_report.csv'
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(i for i in headers)
            for j in data:
                writer.writerow(j)

    def print(data, headers, format, logger):
        headers = [x.upper() for x in headers]
        if 'json' in format:
            Output.print_json(data, headers)
        elif 'tree' in format:
            Output.print_tree(data, headers)
        elif 'csv' in format:
            Output.csv_out(data, headers)
        else:
            Output.print_table(data, headers)