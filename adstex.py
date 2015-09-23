#!/bin/python3

#ADS LaTeX reference finder

#(C) Tom Hands 2015 tom.hands@le.ac.uk
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import re #Regular expression search
import urllib.request
import urllib.parse
import json
import sys

apitoken = "UJHKnhig9MTC9mPECsFVAAiNayvaFE8Kr7xwnJmt"
journal_dict = { "MNRAS" : 'Monthly Notices of the Royal Astronomical Society', "IAUS" : "IAU Symposium"}

"""def custom_ref(bibcode, trunc_in_text = 1, trunc_in_list = 1):
    print("generating custom reference...")
    query_url = 'http://api.adsabs.harvard.edu/v1/search/query?'
    query = "q=bibcode:"+ref_id+"&fl=title,author,year,pub,bibstem,volume,page"
    ads_req = urllib.request.Request(query_url + query)    
    ads_req.add_header("Authorization", "Bearer "+apitoken)
    resp = urllib.request.urlopen(ads_req)
    data = json.loads(resp.read().decode(resp.info().get_param('charset') or 'utf-8'))
    in_text = 0

    for item in data['response']['docs'][0]["author"]:
        
    #Start building the custom reference...
    ref = "\\bibitem[\\protect\\citeauthoryear"
"""

def request_ref(id, refname=id, db='AST', format="MNRAS"):
    queryurl = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?bibcode='+id+'&data_type='+format+'&return_fmt=LONG&db_key='+db
    #print(queryurl)
    ads_req = urllib.request.Request(queryurl)  
    resp = urllib.request.urlopen(ads_req)
    response_string = resp.read().decode(resp.info().get_param('charset') or 'utf-8')
    #print(response_string)
    print(response_string[response_string.find('\\'):-2])
    return(response_string[response_string.find('\\'):-1].replace(id,refname))

def author_parse(authorlist):
    authors = []
    author_split = re.findall('[A-Z][A-Z][a-z]+', authorlist)
    print(authorlist)
    print(author_split)
    author_q = "("
    for item in author_split:
        author_q = author_q +"\"" + item[1:] + ",+" + item[0] +  "\","
    author_q = author_q + ")"
    print(author_q)
    author_q = urllib.parse.quote(author_q)
    #author_q = '%22Hands,+T%,Alexander,+R22'
    print(author_q)
    return author_q

def get_ref(ref_id):
    query_url = 'http://api.adsabs.harvard.edu/v1/search/query?'
    if ref_id[0].isnumeric(): #Bibcode
        #print("bibcode search for id " + ref_id)
        query = "q=bibcode:"+ref_id+"&fl=title,author,year,bibstem,pub,database,bibcode"
    else: #Author search
        print(re.search('[0-9]+', ref_id).group(0))
        paper_year = re.search('[0-9]+', ref_id).group(0)
        split = re.split(paper_year, ref_id)
        paper_author = split[0]
        paper_journal = split[1]
        #if paper_journal in journal_dict:
        #    paper_journal = journal_dict[paper_journal]
        author_query = author_parse(paper_author)
        query = "q=author:"+author_query+"&fq="+paper_year+"&fl=title,author,year,bibstem,pub,database,bibcode"
        if paper_journal != "":
            query = query + "&fq=bibstem:" +  urllib.parse.quote(paper_journal)
    ads_req = urllib.request.Request(query_url + query)    
    ads_req.add_header("Authorization", "Bearer "+apitoken)
    resp = urllib.request.urlopen(ads_req)
    data = json.loads(resp.read().decode(resp.info().get_param('charset') or 'utf-8'))
    #print(data)
    print("Matched paper " + data['response']['docs'][0]["title"][0] + " pub in " + data['response']['docs'][0]["pub"] + " by " + str(data['response']['docs'][0]["author"])  )
    filter = "AST"
    if data['response']['docs'][0]["database"] == "physics":
        filter = "PHY"
    elif data['response']['docs'][0]["database"] == "general":
        filter = "GEN"
    return request_ref(data['response']['docs'][0]["bibcode"], ref_id, filter)

def parse_aux(filename):
    f = open(filename)
    aux = f.read();
    f.close()
    m = re.findall('(?<=\\citation{).+(?=})', aux)
    print(m)
    return m

def generate_bib(filename):
    references = parse_aux(filename)
    full_refs = []
    bib_file_name = filename.split(".")[0] + ".bbl"
    f = open(bib_file_name, 'w')
    f.write("\\begin{thebibliography}{"+str(len(full_refs))+"}\n")
    for ref in references:
        f.write(get_ref(ref))
    f.write("\n\\end{thebibliography}")
    f.close()
    

generate_bib(sys.argv[1]+".aux")
#get_ref("THands2014MNRAS")
#get_ref("2014MNRAS.445..749H")
#http://stackoverflow.com/questions/13921910/python-urllib2-receive-json-response-from-url
#parse_aux("/home/t/toh1/Dropbox/Jobs/research_statement.aux")

#print(resp.read().decode("utf-8"))
#ast.literal_eval(resp.read().decode("utf-8"))
