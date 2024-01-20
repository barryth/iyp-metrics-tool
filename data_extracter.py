# A supporting method that collects and combines all domain names of 2 datasets, depicting the most visited sites
# in the Netherlands
# Dataset 1 is taken from the Semrush website: https://www.semrush.com/trending-websites/nl/all
# and is a txt copy of the list given by the link
#
# Dataset 2 is a csv available here: https://radar.cloudflare.com/domains/nl
#
# This file gets all domain names given by these sources, and combines the list, removing duplicates.

def get_domains():
    semrush_data = open('data/semrush_data.txt', mode='r')
    semrush_array = semrush_data.read().split("\n")
    semrush_domains_only = []
    for i in range(len(semrush_array)):
        if (i % 8 == 0):
            semrush_domains_only.append(semrush_array[i])


    cloudflare_data = open('data/cloudflare-radar-domains-top-100-nl-20240117.csv')
    cloudflare_array = cloudflare_data.read().split(',')

    cloudflare_domains_only = []
    for i in range(3, len(cloudflare_array)):
        if (i % 2 == 1):
            cloudflare_domains_only.append(cloudflare_array[i])



    combined_array = semrush_domains_only.copy()
    for domain in cloudflare_domains_only:
        if domain not in combined_array:
            combined_array.append(domain)

    return combined_array