# My experimental project on Force directed graphs
# based on http://www.austintaylor.io/d3/python/pandas/2016/02/01/create-d3-chart-python-force-directed/
# methods but instead of Les Misérables or Network traffic data, I used Wikipedia's 2017 movie data

import pandas as pd,requests,json
from io import StringIO

# wikipedia has months in the below format & we need to remove them for plotting
months = ['J A N U A R Y',
          'F E B R U A R Y',
          'M A R C H',
          'A P R I L',
          'M A Y',
          'J U N E',
          'J U L Y',
          'A U G U S T',
          'S E P T E M B E R',
          'O C T O B E R',
          'N O V E M B E R',
          'D E C E M B E R']


p = requests.get('https://en.wikipedia.org/wiki/2017_in_film').text  #just change the year to get that years data
a = pd.read_html(StringIO(p), attrs={"class":"wikitable"})

# the last 4 dataframes in list 'a' contain our movie data
p = []
for t in a[-4:] :
    t.columns = t.iloc[0]
    t = t.reindex(t.index.drop(0))
    c = list(t.columns)
    t = t[c[:5]]
    
    # we will be transposing the dataframes
    # this below loop is used to create headers for it
    # as transposing will created headers from the index which is numeric
    t['A'] = pd.Series('row_'+str(i) for i in range(len(t)))
    t.set_index('A', inplace=True)
    
    # dataframe now has values in rows that are not needed,
    # so we need to shift them left, since we need the remaining data
    # but shifting rows is not directly possible,so...
    # transpose the dataframe, now we can shift the columns 
    x = t.T 
    for i in x.columns:
        if x[i][0] in months or x[i][0].isnumeric():
            x[i] = x[i].shift(-1)
    for i in x.columns: #doing again to remove numbers(openings data) left behind by the months
        if x[i][0] in months or x[i][0].isnumeric():
            x[i] = x[i].shift(-1)
    
    # transposing again to bring the table back to its original shape
    t = x.T
    t = t[['Opening', 'Studio']]
    t = t.rename(columns={'Opening' : 'Title', 'Studio' : 'Cast'})
    p.append(t)

a = p[0].append([p[1],p[2],p[3]],ignore_index=True)

movie_actor_dict = {}
movie_director_dict = {}
movie_sw_dict = {}

actors, directors, sps = [], [], []
nodes, links = [], []

# 'nodes list' will contain unique elements or nodes to be plotted in graph
# nodes list will have movies, actors, directors, screenwriters as elements.

# 'links list' will contain the relationship information like
#  which actors acted in which movies and so on


# this is interesting part where we split our 'cast and crew' data 
# into 'directors' , 'actors' and 'screenplay' elements
# the Wikipedia does not give us uniformly formatted data
# so, processing it requires some string manipulation

for mov,i in a.itertuples(index=False):
    nodes.append({'name':mov,'group':1})
    tmp = i.split(';')
    if len(tmp) == 1:
        pos = i.find(')')
        if pos == -1:
            movie_actor_dict[mov] = i.split(',')
        else:
            movie_actor_dict[mov] = i[pos+2:].split(',')
            movie_director_dict[mov] = i[:pos+1].split(',')
    elif len(tmp) == 2:
        var1 = tmp[0].split(',')
        for o in var1:
            if '(screenplay)' in o:
                movie_sw_dict[mov] = [o]
                var1.remove(o)
            movie_director_dict[mov] = var1
        movie_actor_dict[mov] = tmp[1].split(',')
    else:
        for j in tmp:     
            if 'director' in j:
                movie_director_dict[mov] = j.split(',')
            elif '(screenplay)' in j:
                movie_sw_dict[mov] = j.split(',')
            else:
                movie_actor_dict[mov] = j.split(',')

for movie,director in movie_director_dict.items():
    for i in director:
        b = i.find('(')
        if b == -1:
            i = i+'(D)'  # removing the '(director)' and replacing it with just (D)
        else:
            i = i[:b-1]+'(D)'
        links.append({'source':movie,'target':i.strip(),'value':1})
        if i not in directors:
            directors.append(i)
for i in directors:
    nodes.append({'name':i.strip(),'group':2})


for movie,sw in movie_sw_dict.items():
    for i in sw:
        b = i.find('(')
        if b==-1:
            i=i+'(SP)'  # removing the '(screenplay)' and replacing it with just (SP)
        else:
            i=i[:b-1]+'(SP)'
        links.append({'source':movie,'target':i.strip(),'value':1})
        if i not in sps:
            sps.append(i)
for i in sps:
    b = i.find('(')
    nodes.append({'name':i.strip(),'group':3})


for movie,actor in movie_actor_dict.items():
    for i in actor:
        links.append({'source':movie,'target':i.strip(),'value':1})
        if i not in actors:
            actors.append(i)
for i in actors:
    nodes.append({'name':i.strip(),'group':4})

new={}
for c,i in enumerate(nodes):
    new[i['name']] = c

# the below loop prepares the data in the desired format
nlinks=[]
for i in links:
    xx = {'source' : new[i['source']], 'target' : new[i['target']], 'value' : 1}
    nlinks.append(xx)

# finally writing our data as json file to be used in the html.
json_dump = json.dumps({"nodes":nodes, "links":nlinks}, indent=1, sort_keys=True)
json_out = open('/home/nav/Desktop/export.json','w')
json_out.write(json_dump)
json_out.close()
