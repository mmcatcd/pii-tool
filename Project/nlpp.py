

nlp = spacy.load('en_core_web_sm')
df = pd.read_csv('people.csv')

for val in df['name']:
    doc = nlp(val)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            print(ent.text)