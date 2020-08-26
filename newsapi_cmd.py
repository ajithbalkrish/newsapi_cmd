# importing the required modules
import os
import argparse
import newsapi_wrapper as nw
import pandas as pd
import yaml
from dotenv import load_dotenv

def write_env(args):
    fname = '.env'
    try:
        # Can make generic
        with open(fname, "wt") as file:
            file.write('NEWSAPI_KEY=\"{}\"'.format(args[0]))
            file.write('\n')
            file.write('RESULTS_PATH=\"{}\"'.format(args[1]))
            file.write('\n')
    except Exception as e:
        print(e)

def get_all_news(args):
    print('get_all_news')

def top_headlines(args):
    print('top_headlines')
    try:
        load_dotenv()
        #load_env()
        with open(args[0], 'r') as file:
            params = yaml.safe_load(file)
        news = nw.NewsApiWrapper(os.getenv("NEWSAPI_KEY"), os.getenv("RESULTS_PATH"))
        news.get_top_headlines_html(**params)
    except Exception as e:
        print(e)
        
def check_setup():
    if not os.path.exists('.env'):
        print('Setup is not done.')
        print('Run => news_feeds.py --setup newsapi_key data_loc')
        exit()
    #load_env()
    load_dotenv()
    if not os.getenv("NEWSAPI_KEY"):
        print('Setup is not done.')
        print('Run => news_feeds.py --setup newsapi_key data_loc')
        exit()

def main():
    # create parser object
    parser = argparse.ArgumentParser(description = "A news feed aggregator!")

    # defining arguments for parser object 
    parser.add_argument("-t", "--topnews", type=str, nargs=1,
                        metavar = ('input_file'),
                        help = "Get top headlines based on the query.")
    parser.add_argument("-a", "--allnews", type=str, nargs=1,
                        metavar = ('input_file'),
                        help = "Get all headlines based on the query.")
    parser.add_argument("-s", "--setup", type = str, nargs = 2,
                        metavar = ('newsapi_key','data_loc'),
                        help="newsapi_key: API key from https://newsapi.org/; data_loc: directory to save query results")
                        
    # parser.add_argument("-t", "--top_headlines", type = str, nargs = ,
    #                     metavar = "file_name", default = None,
    #                     help = "Opens and reads the specified text file.")

    # parse the arguments from standard input
    args = parser.parse_args()
    if args.setup == None:
        check_setup()
    # calling functions depending on type of argument
    if args.setup != None:
            write_env(args.setup)
    elif args.topnews != None:
            top_headlines(args.topnews)
    elif args.allnews != None:
            get_all_news(args.allnews)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

#NEWSAPI_KEY='d8d4416f2cc543f08186ea5b07f352c3'
#RESULTS_PATH: "/Volumes/Data-2/Data Science/Projects/News/Results/"

