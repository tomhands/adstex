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

def request_ref(id, refname=id, db='AST', data_type="MNRAS", format="G"):
    #queryurl = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?bibcode='+id+'&data_type='+format+'&return_fmt=LONG&db_key='+db
    queryurl = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?bibcode='+id+'&data_type='+data_type+'&format='+urllib.parse.quote(format)+'&return_fmt=LONG&db_key='+db
    ads_req = urllib.request.Request(queryurl)  
    resp = urllib.request.urlopen(ads_req)
    response_string = resp.read().decode(resp.info().get_param('charset') or 'utf-8')
    print(response_string[response_string.find('\\'):-2])
    return(response_string[response_string.find('\\'):-1].replace(id,refname))

def author_parse(authorlist):
    authors = []
    author_split = re.findall('[A-Z][A-Z][a-z]+', authorlist)
    author_q = "("
    for item in author_split:
        author_q = author_q +"\"" + item[1:] + ",+" + item[0] +  "\","
    author_q = author_q + ")"
    author_q = urllib.parse.quote(author_q)
    return author_q

def get_ref(ref_id):
    query_url = 'http://api.adsabs.harvard.edu/v1/search/query?'
    print("=========================================================================")
    print("Attempting to find match for latex reference " + ref_id)
    if ref_id[0].isnumeric(): #Bibcode
         query = "q=bibcode:"+ref_id+"&fl=title,author,year,bibstem,pub,database,bibcode"
    else: #Author search
        paper_year = re.search('[0-9]+', ref_id).group(0)
        split = re.split(paper_year, ref_id)
        paper_author = split[0]
        paper_journal = split[1]
        author_query = author_parse(paper_author)
        query = "q=author:"+author_query+"&fq=year:"+paper_year+"&fl=title,author,year,bibstem,pub,database,bibcode"
        if paper_journal != "":
            query = query + "&fq=bibstem:" +  urllib.parse.quote(paper_journal)
    ads_req = urllib.request.Request(query_url + query)    
    ads_req.add_header("Authorization", "Bearer "+apitoken)
    resp = urllib.request.urlopen(ads_req)
    data = json.loads(resp.read().decode(resp.info().get_param('charset') or 'utf-8'))
    if len(data['response']['docs']) == 0:
        print("Unable to match provided reference to an article!")
        return False
    if len(data['response']['docs']) > 1:
        print("Warning! Reference was ambiguous, " + str(len(data['response']['docs'])) + " articles found.")
    print("Matched reference " + ref_id + " with ADS entry \n\t"  + data['response']['docs'][0]["title"][0] + "\n\tpublished in " + data['response']['docs'][0]["pub"] + "\n\tby " + str(data['response']['docs'][0]["author"])  )
    filter = "AST"
    if data['response']['docs'][0]["database"] == "physics":
        filter = "PHY"
    elif data['response']['docs'][0]["database"] == "general":
        filter = "GEN"
    f = open("customcitationformat")
    format = f.read()
    f.close()
    return (int(data['response']['docs'][0]["year"]), data['response']['docs'][0]["author"], request_ref(data['response']['docs'][0]["bibcode"], ref_id, filter, "Custom", format))

def parse_aux(filename):
    f = open(filename)
    aux = f.read();
    f.close()
    m = re.findall('(?<=\\citation{).+(?=})', aux)
    m = set(m)
    print(m)
    return m

#def paper_comparison
def generate_bib(filename):
    references = parse_aux(filename)
    full_refs = []
    bib_file_name = filename.split(".")[0] + ".bbl"
    f = open(bib_file_name, 'w')
    f.write("\\begin{thebibliography}{"+str(len(full_refs))+"}\n")
    #Pull references from ADS
    for ref in references:
        full_ref = get_ref(ref)
        if full_ref != False:
            full_refs.append(full_ref)
    full_refs = sorted(full_refs, key = lambda x: x[1][0]) #Sort by first author
    #Write references to file
    for ref in full_refs:
        f.write(ref[2])
    f.write("\n\\end{thebibliography}")
    f.close()
    
generate_bib(sys.argv[1]+".aux")
