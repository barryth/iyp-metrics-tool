# A Python script to compare two datasets on their Anycast data:
# Data of BGPtools, and data received from the University of Twente

from port import query_neo4j
import data_extracter
import pandas as pd
import io
import json
import re

# Queries a given domain list on their prefixes and anycast data
def query_anycast(query_domain_list):
    query = """MATCH (dn:DomainName) 
               WHERE dn.name in """ + str(query_domain_list) + """ 
               MATCH (dn)-[:RESOLVES_TO]-(ip2:IP)-[p:PART_OF]-(pfx:Prefix) 
               RETURN dn.name, collect(distinct pfx) as px, EXISTS((:Tag{label: 'Anycast'})-[:CATEGORIZED]-(pfx)) AS Anycast"""

    response = query_neo4j(query)
    return response


def convert_json(json_response):
    return pd.read_json(io.StringIO(json_response))

def get_domain_list():
    return data_extracter.get_domains()

# Neo4j's response
response_json = query_anycast(get_domain_list())

# Normalizes the database output to have a distinct domain name & prefix combination
df = pd.json_normalize(json.loads(response_json))
df = df.explode('px').reset_index(drop=True)
df = df.merge(pd.json_normalize(df['px']), left_index=True, right_index=True).drop('px', axis=1)

# As the UTwente data only contains ipv4 & /24 prefixes, filter the BGPtools data on this
df4 = df.loc[df['af'] == 4]
df_any = df4.loc[df4['prefix'].str[-3:] == '/24']

# Read UTwente's Anycast data
anycast_data = open('data/ark_anycast_icmp.txt', mode='r')
anycast_list = anycast_data.read().split("\n")

# Removes the last 8 bits of the IP Address (or everything from the last dot onwards)
# So for example, 130.89.1.169 becomes 130.89.1
find = re.compile("^(.*)\..*")
utwente_anycast_24_list = []
for ip in anycast_list[:-1]:
    utwente_anycast_24_list.append(re.match(find, ip).group(1))

# Removes all Prefixes in dataset that are not included in UTwente's data
dfw = df_any.loc[df['prefix'].str[:-5].isin(utwente_anycast_24_list)]
# Prints all prefixes of domains in our set of domains that UTwente's data sees as deploying anycast.
print(dfw)

# Creates a df with all domains of which BGPtools says their anycasting
anycast_true_df = df.loc[df['Anycast'] == True]

# Removes all prefixes that are not /24
anycast_true_24_list = anycast_true_df.loc[anycast_true_df['prefix'].str[-3:] == '/24']

# Creates a df of all domains false positively identified by BGPtools as being anycasting, according to UTwente's data
bgp_false_positive = anycast_true_24_list.loc[~anycast_true_24_list['prefix'].str[:-5].isin(utwente_anycast_24_list)]

# Prints all false positives (none)
print(bgp_false_positive)