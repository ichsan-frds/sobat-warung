import pandas as pd

rules = pd.read_csv('./data/association_rules.csv')

rules['antecedents'] = rules['antecedents'].apply(lambda x: [i.strip() for i in str(x).split(",")])
rules['consequents'] = rules['consequents'].apply(lambda x: [i.strip() for i in str(x).split(",")])

def get_bundling(product: str, top_n: int = 1):
    recs = rules[rules['antecedents'].apply(lambda x: product in x)]
    recs = recs.sort_values(by="confidence", ascending=False)
    result = recs.head(top_n)[['antecedents', 'consequents', 'confidence', 'lift']]
    
    return result.to_dict(orient='records')