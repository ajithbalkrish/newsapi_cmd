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
logger = logging.getLogger('newsapiCmd')

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
                                 logger=logger)
        if action == 'topnews':
            html_path = news.get_top_headlines_html(**params)
        elif action == 'allnews':
            html_path = news.get_all_news(**params)
        elif action == 'sources':
            html_path= news.get_sources(**params)
        else:
            raise logger.exception("Invalid acttion passed to query")
        print('Results saved in {}'.format(html_path) )
        logger.debug('Results saved in {}'.format(html_path))
    except Exception as e:
        logger.exception(e, exc_info=True)
        
def check_setup():
    if not os.path.exists('.env'):
        print('Setup is not done.')
        print('Run => news_feeds.py --configure newsapi_key data_loc')
        exit()
    load_dotenv()
    if not os.getenv("NEWSAPI_KEY"):
        print('Setup is not done.')
        print('Run => news_feeds.py --configure newsapi_key data_loc')
        exit()

def main():  
    # Help strings 
    TEMPLATE_PATH = './newsapi_wrapper/Templates/' 
    all_tmplt = TEMPLATE_PATH+'get_everything_query_template.yaml'
    allnews_help = "get all news headlinesbased on the query; \
        template for input file: {}.".format(all_tmplt)

    top_tmplt = TEMPLATE_PATH+'top_headlines_query_template.yaml'
    topnews_help = "get top news headlines based on the query; \
        template for input file: {}.".format(top_tmplt)

    sources_tmplt = TEMPLATE_PATH+'source_query_template.yaml'
    sources_help = "return the available news publishers; template \
        for input file: {}.".format(sources_tmplt)
    
    config_help = 'newsapi_key: API key from newsapi.org; data_loc: \
        directory to save query results'

    # create parser object
    parser = argparse.ArgumentParser(description \
        = "Command line utility to explore news APIs from newsapi.org")
    # defining arguments for parser object 
    parser.add_argument("-c", "--configure", type=str, nargs=2,
                        metavar=('newsapi_key','data_loc'),
                        help=config_help)
    parser.add_argument("-t", "--topnews", type=str, nargs=1,
                        metavar=('input_file'), help=topnews_help)
    parser.add_argument("-a", "--allnews", type=str, nargs=1,
                        metavar=('input_file'), help=allnews_help)
    parser.add_argument("-s", "--sources", type=str, nargs=1,
                        metavar=('input_file'), help=sources_help)

    # parse the arguments from standard input
    args = parser.parse_args()
    if args.configure == None:
        check_setup()
    # call functions depending on type of argument
    if args.configure != None:
        write_env(args.setup)
    elif args.topnews != None:
        query('topnews', args.topnews)
    elif args.allnews != None:
        query('allnews', args.allnews)
    elif args.sources != None:
        query('sources', args.sources)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


