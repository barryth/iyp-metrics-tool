# A Python script to collect DNS resilience metrics on a list of domains
# through the Internet Yellow Pages
import pandas as pd
import io
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from port import query_neo4j
import data_extracter


def query_database(query_domain_list):

    query = """MATCH (dn:DomainName) 
            WHERE dn.name in """ + str(query_domain_list) + """
            MATCH (dn)-[m:MANAGED_BY]-(ans:AuthoritativeNameServer)-[rt:RESOLVES_TO]-(ip2:IP)-[p:PART_OF]-
            (px:Prefix)-[o:ORIGINATE | ROUTE_ORIGIN_AUTHORIZATION]-(a:AS)
            RETURN dn.name, COUNT(DISTINCT(ans)), COUNT(DISTINCT(px)), COUNT(DISTINCT(a)), 
            EXISTS((:Tag{label: 'Anycast'})-[:CATEGORIZED]-(:Prefix)-[:PART_OF]-(:IP)-[:RESOLVES_TO]-(dn)) AS Anycast"""

    response = query_neo4j(query)
    return response


def convert_json(json_response):
    return pd.read_json(io.StringIO(json_response))


def get_domain_list():
    return data_extracter.get_domains()


domain_list = get_domain_list()
df = convert_json(query_database(domain_list))

print(df)


def get_ns_count_plot():
    asn_count = df['COUNT(DISTINCT(ans))'].value_counts(sort=False).reindex(np.arange(df['COUNT(DISTINCT(ans))'].max()), fill_value=0)
    asn_count.plot.bar()
    plt.savefig('figs/ns_count.png')


def get_ns_px_count_plot():
    ip_count = df['COUNT(DISTINCT(px))'].value_counts(sort=False).reindex(np.arange(df['COUNT(DISTINCT(px))'].max()), fill_value=0)
    ip_count.plot.bar()
    plt.savefig('figs/px_count.png')


def get_as_count_plot():
    as_count = df['COUNT(DISTINCT(a))'].value_counts(sort=False).reindex(np.arange(df['COUNT(DISTINCT(a))'].max()), fill_value=0)
    as_count.plot.bar()
    plt.savefig('figs/as_count.png')


def get_anycast_count_plot():
    ac_count = df['Anycast'].value_counts(sort=False)
    ac_count.plot.pie()
    plt.savefig('figs/anycast_count.png')

if __name__ == "__main__":
    get_ns_count_plot()
    get_ns_px_count_plot()
    get_as_count_plot()
    get_anycast_count_plot()
