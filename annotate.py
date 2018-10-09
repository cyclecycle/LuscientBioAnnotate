import requests
import json
import pandas as pd
import numpy as np
import spotlight
from SPARQLWrapper import SPARQLWrapper, JSON


class Annotator():

    def __init__(self):
        pass

    def pubtator_annotations(self, pmid):
        base = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept'
        retmode = 'json'
        pmid = str(pmid)
        url = '{0}/{1}/{2}' .format(base, pmid, retmode)
        r = requests.get(url).text
        j = json.loads(r)
        text = j[0]['text']
        pbt_ann = []
        pbt2class = {
            'gene': 'biomolecule',
            'species': 'species',
            'chemical': 'chemical',
            'disease': 'disease',
            'mutation': 'biomolecule'
        }
        for a in j[0]['denotations']:
            pbt_class = a['obj'].split(':')[0].lower()
            try:
                mapped_class = pbt2class[pbt_class]
                pass
            except:
                print('Unmapped class: ', pbt_class)
                mapped_class = np.nan
            strt = a['span']['begin']
            end = a['span']['end']
            term = text[strt:end]
            pbt_ann.append({
                'term': term,
                'pubtator_class': pbt_class,
                'pubtator_mapped_class': mapped_class,
                'pubtator_offset': strt
            })
        pbt = pd.DataFrame(pbt_ann).set_index('term')
        self.pubtator = pbt
        return pbt

    def dbpedia_annotations(self, text):
        base = 'https://api.dbpedia-spotlight.org/en/annotate'
        annotations = spotlight.annotate(base, text, confidence=0.4, support=5)
        sparql = SPARQLWrapper('http://dbpedia.org/sparql')
        sparql.setReturnFormat(JSON)

        dbp2class = {  # Map dbpedia types to our standard classes
            'biomolecule': 'biomolecule',
            'protein': 'biomolecule',
            'species': 'species',
            'eukaryote': 'species',
            'animal': 'species',
            'mammal': 'species',
            'disease': 'disease',
            'anatomicalstructure': 'anatomy'
        }

        dbp_ann = {}
        for a in annotations:
            term = a['surfaceForm']
            types = a['types'].lower().replace('dbpedia:', '').split(',')
            uri = '<{0}>' .format(a['URI'])
            uri = check_dbp_redirect(sparql, uri)
            types = [t for t in types if t in dbp2class.keys()]
            classes = [dbp2class[t] for t in types]
            dbp_ann[term] = {
                'dbpedia_types': a['types'],
                'dbpedia_mapped_classes': classes,
                'dbpedia_resource': uri,
                'dbpedia_offset': a['offset']
            }
        dbp = pd.DataFrame(dbp_ann).transpose()
        self.dbpedia = dbp
        return dbp

    def bio2rdf_annotations(self, terms):
        sparql = SPARQLWrapper('http://pubmed.bio2rdf.org/sparql')
        sparql.setReturnFormat(JSON)

        query = '''
            SELECT DISTINCT ?concept ?type WHERE {{
            ?concept dcterms:title "{0}"@en .
            ?concept rdf:type ?type .
        }}
        '''
        bio2rdf = {}
        for t in terms:
            q = query.format(t)
            sparql.setQuery(q)
            results = sparql.query().convert()
            if not results:
                continue
            bio2rdf[t] = {
                'bio2rdf_uris': [r['concept']['value'] for r in results['results']['bindings']],
                'bio2rdf_classes': [r['type']['value'] for r in results['results']['bindings']],
            }
        bio2rdf = pd.DataFrame(bio2rdf).transpose()
        self.bio2rdf = bio2rdf
        return bio2rdf


def check_dbp_redirect(sparql, uri):
    q = 'SELECT * WHERE {{ {0} <http://dbpedia.org/ontology/wikiPageRedirects> ?redirect}}'.format(uri)
    sparql.setQuery(q)
    results = sparql.query().convert()
    try:
        uri = '<{0}>' .format(results['results']['bindings'][0]['redirect']['value'])
    except:
        pass
    return uri
