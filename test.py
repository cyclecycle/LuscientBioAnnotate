from pprint import pprint
from annotate import Annotator

annotator = Annotator()

pmid = 29969095
pbt = annotator.pubtator_annotations(pmid)
pprint(pbt)

text = '''
Neurogenic decisions require a cell cycle independent function of the CDC25B phosphatase. A fundamental issue in developmental biology and in organ homeostasis is understanding the molecular mechanisms governing the balance between stem cell maintenance and differentiation into a specific lineage. Accumulating data suggest that cell cycle dynamics play a major role in the regulation of this balance. Here we show that the G2/M cell cycle regulator CDC25B phosphatase is required in mammals to finely tune neuronal production in the neural tube. We show that in chick neural progenitors, CDC25B activity favors fast nuclei departure from the apical surface in early G1, stimulates neurogenic divisions and promotes neuronal differentiation. We design a mathematical model showing that within a limited period of time, cell cycle length modifications cannot account for changes in the ratio of the mode of division. Using a CDC25B point mutation that cannot interact with CDK, we show that part of CDC25B activity is independent of its action on the cell cycle.
'''

dbp = annotator.dbpedia_annotations(text)
pprint(dbp)

df = pbt.join(dbp, how='outer')

terms = df.index
bio2rdf = annotator.bio2rdf_annotations(terms)
print(bio2rdf)

df = df.join(bio2rdf)
