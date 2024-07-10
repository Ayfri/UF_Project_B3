import pandas as pd

event_codes = pd.read_json('data/cameo_mapping_fr.json', orient='index')
event_codes = event_codes.rename(columns={0: 'Description'})
event_codes = event_codes.reset_index().rename(columns={'index': 'EventCode'})
event_codes['Description'] = event_codes['Description'].str.title()


def add_event_code_names(df: pd.DataFrame) -> pd.DataFrame:
	df['EventCode'] = df['EventCode'].astype('int64')
	df = df.merge(event_codes, on='EventCode', how='left')
	return df
