import parsel
import urllib
import pandas as pd
import argparse
from tqdm import tqdm
import logging

if __name__ == '__main__': 
    parser = argparse.ArgumentParser()
    parser.add_argument('country', help='two-letter  country code')
    parser.add_argument('-q', help='search query', default='data scientist')
    parser.add_argument('--pages', '-p', help='max page', default='1000', type=int)


    args = parser.parse_args()

    BASE_URL = 'http://{}.indeed.com'.format(args.country)
    if args.country == 'us':
        BASE_URL = 'http://.indeed.com'
    
    params = {
        'q': args.q,
        'jt': 'fulltime',
        'sort': 'date'
    }

    jobs = []
    for page in tqdm(range(1, args.pages, 10)): 
        params['start'] = page
        encoded_params = urllib.parse.urlencode(params)

        url = "{}/jobs?{}".format(BASE_URL, encoded_params)
        logging.debug(url)
        text = urllib.request.urlopen(url)
        Selector = parsel.Selector(text.read().decode()) 

        for el in Selector.css('.row.result'):
            job = {}
            job['company_name'] = el.xpath('string(.//*[@class="company"])').get().strip()
            job['title'] = el.xpath('string(.//h2/*)').get()
            job['link'] = "{}{}".format(BASE_URL, el.css('a').attrib['href'])
            job['address'] = el.xpath('.//*[@data-rc-loc]').attrib['data-rc-loc']
            job['salary'] = el.css('.salary::text').get()
            job['summary'] = el.css('.summary').xpath('string(.)').get().strip()

            logging.debug(job)
            jobs.append(job)

    df = pd.DataFrame(jobs)
    
    df.to_csv('{}__{}.csv'.format(args.country, args.q), index=False)