# importing the required modules
import os
import argparse
import pandas as pd
import yaml
import logging
from logging.config import fileConfig
from dotenv import load_dotenv

import newsapi_wrapper as nw

# Configure logging
fileConfig('newsapi_cmd_log.ini')
logger = logging.getLogger('newsapiLogger')

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

def query(action, args):
    logger.debug('top_headlines')
    try:
        load_dotenv()
        with open(args[0], 'r') as file:
            params = yaml.safe_load(file)
        news = nw.NewsApiWrapper(os.getenv("NEWSAPI_KEY"), 
                                 os.getenv("RESULTS_PATH"),
                                 logger=logger
                                )
        if action == 'topnews':
            html_path = news.get_top_headlines_html(**params)
        elif action == 'allnews':
            html_path = news.get_all_news(**params)
        else:
            raise logger.exception("Invalid acttion passed to query")
        print('Results saved in {}'.format(html_path) )
    except Exception as e:
        logger.exception(e, exc_info=True)
        
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
    # Help strings  
    all_tmplt = './newsapi_wrapper/Templates/get_everything_query_template.yaml'
    allnews_help = "Get news headlines; use {} as template for input file.".format(all_tmplt)
    top_tmplt = './newsapi_wrapper/Templates/top_headlines_query_template.yaml'
    topnews_help = "Get news headlines; use {} as template for input file.".format(top_tmplt)
    setup_help = 'newsapi_key: API key from newsapi.org; data_loc: directory to save query results'

    # create parser object
    parser = argparse.ArgumentParser(description = "A news feed aggregator!")
    # defining arguments for parser object 
    parser.add_argument("-t", "--topnews", type=str, nargs=1,
                        metavar=('input_file'), help=topnews_help)
    parser.add_argument("-a", "--allnews", type=str, nargs=1,
                        metavar=('input_file'), help=allnews_help)
    parser.add_argument("-s", "--setup", type=str, nargs=2,
                        metavar=('newsapi_key','data_loc'),
                        help=setup_help)
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
        query('topnews', args.topnews)
    elif args.allnews != None:
        query('allnews', args.allnews)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


