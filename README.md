**newsapi_cmd.py**
A Python command line utility to explore news APIs from newsapi.org.
Copyright (c) 2020-2022 Ajith Balakrishnan ajith.balakrish@gmail.com
News API Terms of Service can be found in https://newsapi.org/terms.

------------
**Installation: **
- Download the source files
- Create a python3 virtual enviroment
> $ python3 -m venv <path_to_virtual_env>
$ source <path_to_virtual_env>/bin/activate
- Install reuired Python libraries
> $ pip install -r requirements.txt
------------
**Usage:**
> $ newsapi_cmd.py [-h] [-c newsapi_key data_loc] [-t input_file] [-a input_file] [-s input_file]

**Arguments:** 
- -h, --help  show this help message and exit
- -c newsapi_key data_loc, --configure newsapi_key data_loc
newsapi_key: API key from newsapi.org 
data_loc: directory to save query results
- -t input_file, --topnews input_file
get top news headlines based on the query.
Template for input file in ./newsapi_wrapper/Templates/top_headlines_query_template.yaml.
- -a input_file, --allnews input_file get all news headlinesbased on the query.
Template for input file in ./newsapi_wrapper/Templates/get_everything_query_template.yaml.
- -s input_file, --sources input_file return the available news publishers.
Template for input file in ./newsapi_wrapper/Templates/source_query_template.yaml.

On succes, the results are saved under the directory data_loc.

