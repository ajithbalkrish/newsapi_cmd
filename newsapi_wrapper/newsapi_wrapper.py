#!/usr/bin/env python
# coding: utf-8

import time
import os
import json
import shutil
import pandas as pd
from pandas import json_normalize
from newsapi import NewsApiClient
from datetime import datetime, timedelta, date

pd.options.display.float_format = '{:.2f}'.format
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 100)


TEMPLATE_PATH = "./Templates/"
DATA_PATH = "./Data/"
HTML_TEMPLATE = "query_result_template.html"
PAGE_SIZE = 10


class NewsApiWrapper:
    #
    # Constructor
    #    
    def __init__(self, api_key, results_dir):
        """
        Default arguments:
            api_key: News API key
            results_dir: Directory to save query results
        Keyword arguments passed in query_args:
            :
        """
        if not os.path.exists(results_dir):
            raise Exception("ERROR: Directory does not exist: {}".format(results_dir))
        self._results_dir = results_dir
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._template_dir = dir_path + TEMPLATE_PATH.lstrip('.')
        self._data_dir = dir_path + DATA_PATH.lstrip('.')
        self._html_template = HTML_TEMPLATE
        self._pgsize = PAGE_SIZE
        print('results_dir: {}'.format(results_dir))
        print('api_key: {}'.format(api_key))
        try:
            self._newsapi = NewsApiClient(api_key=api_key)
            self._newsapi_calls = {'get_top_headlines': self._newsapi.get_top_headlines,
                                    'get_everything': self._newsapi.get_everything}
        except:
            print('ERROR: Failed to initialize NewsApiClient')
            raise
                

    #
    # Private methods
    #
    def _cleanup_article_df(self, article_df):   
        new_cols={'author':'Author', 'title':'Title', 'description':'Summary', 
                  'url': 'URL','urlToImage':'URL to Image', 'publishedAt':'Date', 
                  'content': 'Content', 'source.name': 'Source'}
        new_order = ['Date','Title', 'Summary', 'Author', 'Source', 'Content',
                     'URL', 'URL to Image']
        article_df = article_df.rename(columns=new_cols)
        article_df['Date'] = article_df['Date'].astype('datetime64[D]')
        return article_df[new_order]
 
    def _persist_query_response_blob(self, data, fname):
        path = self._data_dir+fname+'.json'
        try:
            with open(path, "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(e)

    def _read_persisted_reponse_blob(self, fname):
        try:
            path = self._data_dir+fname
            with open(path, "r") as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(e)
            return ''
    def _read_html_template(self):
        try:
            path = self._template_dir + self._html_template
            with open(path, "r") as file:
                data = file.read()
                return data
        except Exception as e:
            print(e)
            return ''

    def _create_df_from_article_list(self, articles):
        df = json_normalize(articles)
        return self._cleanup_article_df(df)

    def _make_clickable(self, df):
        title = df['Title']
        url = df['URL']
        return f'<a href="{url}">{title}</a>'

    def _build_query_string(self, query_data):
        value = query_data.pop('Date')
        string = "Date: "+value+"<br>"
        for key, value in query_data.items():
            temp = '{}: {} <br>'.format(key, value)
            string += temp
        return string

    def _save_query_response_html(self, article_df, query_data, fname):
        dst_css = self._results_dir+'style.css'
        if not os.path.exists(dst_css):
            shutil.copyfile(self._template_dir + 'style_template.css', dst_css)
        try:
            path = self._results_dir+fname+'.html'
            query_string = self._build_query_string(query_data)
            html_template = self._read_html_template()
            article_df['Title'] = article_df.apply(lambda article_df: 
                                                    self._make_clickable(article_df), 
                                                    axis=1)
            df = article_df[['Date','Title', 'Summary', 'Author', 'Source']]
            table = df.to_html(escape=False, index=False)
            with open(path, "w") as file:
                file.write(html_template.format(query=query_string,
                                                result=table))
            return path                                    
        except Exception as e:
            return str(e)

    def _validate_response(self, result, api_name):
        if not bool(result):
            raise Exception("ERROR: Empty response from News API {}".format(api_name))
        else:
            status = result['status']
            if status != 'ok':
                raise Exception("ERROR: Not OK status from News API {}".format(api_name))

    def _validate_top_headlines_args(self, **args):
        to_remove = []
        for key, val in args.items():
            if isinstance(val, int) and val == 0:
                to_remove.append(key)
            elif isinstance(val, str) and len(val) == 0:
                to_remove.append(key)
            elif val == None:
                to_remove.append(key)
        for key in to_remove:
            args.pop(key)
        if not 'query_name' in args:
            raise Exception("ERROR: query_name is not provided")
        if 'country' in args and 'sources' in args:
            # you can't mix this country with the sources param
            raise Exception("ERROR: you can't mix country with the sources param: \
                ({}, {})".format(args['country'], args['sources']))
        if 'category' in args and 'sources' in args:
            # you can't mix category with the sources param.
            raise Exception("ERROR: you can't mix category with the sources param: \
                ({}, {})".format(args['category'], args['sources']))
    
        for key, val in args.items():
            print('{}: {}'.format(key, args[key]))
        return args
    #
    # Public methods
    #    
    def query(self, api_name, queryname, persist=True, **query_args):
        print (queryname)
        # Add page size, language to query args
        pgsize = self._pgsize        
        query_args.update(language='en')
        query_args.update(page_size=pgsize)
        # Call corresponding News API 
        #results = self._newsapi.get_top_headlines(**query_args)
        results = self._newsapi_calls[api_name](**query_args)
        # Validate results
        self._validate_response(results, api_name)       
        status = results.pop('status','')
        total_results = results.pop('totalResults', 0)
        # if total results are more than pgsize, repeat query to get
        # all results
        if total_results > pgsize:
            if total_results%pgsize != 0:
                total = total_results + (pgsize - (total_results%pgsize))
            remaining = total//pgsize - 1
            for count in range(remaining):
                pg = count+2
                #next_pg = self._newsapi.get_top_headlines(page=pg, **query_args)
                next_pg = self._newsapi_calls[api_name](page=pg, **query_args)
                self._validate_response(next_pg, api_name)
                results['articles'] += next_pg['articles']
        # Add query name and date to results to save
        query_args.update(query_name=queryname)
        now = date.today()
        query_args.update(Date=now.strftime("%m-%d-%Y"))
        query_args.pop('page_size',0)
        results.update(query=query_args)
        ## Add query status to results to save
        results.update(query_status={'status':status, 'totalResults':total_results})
        if persist:
            self._persist_query_response_blob(results, queryname)
        return results  

    def get_top_headlines_html(self, **query_args):
        """Get top headlines by calling newsapi get_top_headlines with provided arguments.
        Keyword arguments:
            query_name:
                Name of the query. This name will be prefixed in the file name when the results are 
                saved in html and json format.It is manadatory to provide a meaningful query name. 
            country:
                The 2-letter ISO 3166-1 code of the country you want to get headlines for. 
                Possible options: ae ar at au be bg br ca ch cn co cu cz de eg fr gb gr 
                                  hk hu id ie il in it jp kr lt lv ma mx my ng nl no nz 
                                  ph pl pt ro rs ru sa se sg si sk th tr tw ua us ve za . 
                Note: you can't mix this param with the sources param.
            category:
                The category you want to get headlines for. 
                Possible options: business entertainment general health science sports technology . 
                Note: you can't mix this param with the sources param.
            sources
                A comma-seperated string of identifiers for the news sources or blogs you want 
                headlines from. Use the /sources endpoint to locate these programmatically or 
                look at the sources index. Note: you can't mix this param with the country or 
                category params.
            q
                Keywords or a phrase to search for.

        Response:
            Saves results under <results_dir> with name query_name-<timestamp>.html". 
        """
        try:
            args = self._validate_top_headlines_args(**query_args)
            # Get query name and append it with timestamp to use it as html/json filename
            queryname = args.pop('query_name')
            now = datetime.now()
            time = now.strftime("%m_%d_%Y-%H_%M_%S")
            queryname = queryname + '-{}'.format(time)
            # Call get_top_headlines with provided query args
            results = self.query('get_top_headlines', queryname, **args)
            article_df = self._create_df_from_article_list(results['articles'])
            return self._save_query_response_html(article_df, results['query'], queryname)
        except Exception as e:
            print(e)
