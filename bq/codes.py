import json

import pandas as pd

with open('data/cameo_mapping_fr.json', 'r', encoding='utf-8') as f:
	data = json.load(f, object_pairs_hook=lambda pairs: dict(pairs))

event_codes = pd.DataFrame.from_dict(data, orient='index', columns=['Description'])
event_codes = event_codes.reset_index().rename(columns={'index': 'EventCode', 0: 'Description'})
event_codes['Description'] = event_codes['Description'].str.title()


def add_event_code_names(df: pd.DataFrame) -> pd.DataFrame:
	df = df.merge(event_codes, on='EventCode', how='left')
	return df
