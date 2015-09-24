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
    queryurl = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?bibcode='+urllib.parse.quote(id)+'&data_type='+urllib.parse.quote(data_type)+'&return_fmt=LONG&db_key='+db
    #print("Querying reference server: "+ queryurl)
    if data_type != "BIBTEX":
        queryurl = queryurl + '&format='+urllib.parse.quote(format)
    ads_req = urllib.request.Request(queryurl)  
    resp = urllib.request.urlopen(ads_req)
    response_string = resp.read().decode(resp.info().get_param('charset') or 'utf-8')
    #print(response_string[:-2])
    response_string = response_string.split("\n",maxsplit= 4)[4]
    #print(response_string[:-2])
    return(response_string[:-1].replace(id,refname))

def author_parse(authorlist):
    authors = []
    author_split = re.findall('[A-Z]+[a-z]+', authorlist)
    author_q = "("
    if len(author_split) != 0:
        for item in author_split:
            caps = re.split('[a-z]+', item)
            #print(caps)
            extra = "^" if item == author_split[0] else ""
            if len(caps[0]) == 1:
                author_q = author_q +"\"" + extra + item[0:] +  "\","
            elif len(caps[0]) >= 2:
                author_q = author_q +"\"" + extra + item[1:] + ",+" + item[0] +  "\","
    else: #We don't have any caps separated authors...
        author_q = author_q + authorlist
    author_q = author_q + ")"
    author_q = urllib.parse.quote(author_q)
    return author_q

def print_result(result):
    print("\t"  + result["title"][0] + " (" +result["bibcode"] + ")" +"\n\tpublished in " + result["pub"] + "\n\tby " + str(result["author"]))
def get_ref(ref_id, bibtex=False):
    query_url = 'http://api.adsabs.harvard.edu/v1/search/query?'
    which_paper = -1
    print("=========================================================================")
    print("Attempting to find match for latex reference " + ref_id)
    if ref_id[0].isnumeric(): #Bibcode
         query = "q=bibcode:"+ref_id+"&fl=title,author,year,bibstem,pub,database,bibcode"
    else: #Author search
        paper_year = re.search('[0-9]+', ref_id)
        if paper_year == None:
            print("ERROR - You don't appear to have provided a year for this citation... Skipping!")
            return False
        paper_year = paper_year.group(0)
        split = re.split(paper_year, ref_id)
        paper_author = split[0]
        paper_journal = split[1]
        which_paper = re.search('[0-9]+', paper_journal)
        if which_paper==None:
            which_paper = -1
            print("No paper selector specified, assuming first search result is correct")
        else:
            paper_journal = re.split(which_paper.group(0), paper_journal)[0]
            which_paper = int(which_paper.group(0))
            print("Specified paper selector " + str(which_paper) + ", using "  + str(which_paper) + "th search result.")
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
    if len(data['response']['docs']) > 1 and which_paper == -1:
        print("!!!!WARNING!!!!! Reference was ambiguous, " + str(len(data['response']['docs'])) + " articles found.")
        which_paper = 0
        for i,result in enumerate(data['response']['docs'][1:]):
            print("Perhaps you meant: \cite{" + ref_id + str(i + 1) + "}")
            print_result(result)
    elif len(data['response']['docs']) > 1 and which_paper > -1:
        print("There were other references that matched the search, but you wanted this one.")
    print("Matched reference "+ ref_id + " with ADS entry:")
    print_result(data['response']['docs'][which_paper])
    filter = "AST"
    if data['response']['docs'][which_paper]["database"] == ["physics"]:
        filter = "PHY"
    elif data['response']['docs'][which_paper]["database"] == ["general"]:
        filter = "GEN"
    f = open("customcitationformat")
    format = f.read()
    f.close()
    data_type =  "BIBTEX" if bibtex else "Custom"
    return (int(data['response']['docs'][which_paper]["year"]), data['response']['docs'][which_paper]["author"], request_ref(data['response']['docs'][which_paper]["bibcode"], ref_id, filter, data_type, format))

def parse_aux(filename):
    f = open(filename)
    aux = f.read();
    f.close()
    m = re.findall('(?<=\\citation{).+(?=})', aux)
    m = set(m)
    print("List of references required for this document:")
    print(m)
    return m

#def paper_comparison
def generate_bib(filename, bibtex = False):
    references = parse_aux(filename)
    full_refs = []
    extension =".bib" if bibtex else ".bbl"
    bib_file_name = filename.split(".")[0] + extension
    f = open(bib_file_name, 'w')
    data_type = "BIBTEX"
    if not bibtex:
        f.write("\\begin{thebibliography}{"+str(len(full_refs))+"}\n")
    #Pull references from ADS
    for ref in references:
        full_ref = get_ref(ref, bibtex)
        if full_ref != False:
            full_refs.append(full_ref)
    full_refs = sorted(full_refs, key = lambda x: x[1][0]) #Sort by first author
    #Write references to file
    for ref in full_refs:
        f.write(ref[2])
    if not bibtex:
        f.write("\n\\end{thebibliography}")
    f.close()
    
if len(sys.argv) == 3:
    generate_bib(sys.argv[1]+".aux", True)
else:
    generate_bib(sys.argv[1]+".aux")
