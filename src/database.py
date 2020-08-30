from elasticsearch import Elasticsearch, helpers
import datetime
import json
import pandas as pd
from src.logger import logger

class ElasticSearchClass():
    def __init__(self,url='http://localhost:9200'):
        self.url=url
        self.es=Elasticsearch(self.url)

    def ping(self):
        return self.es.ping()

    def create_index_file(self, index_name,folder,text_fields=[], dense_fields=[], dense_fields_dim=512, shards=3, replicas=1):
        index_spec={}

        index_spec['settings']={
            "number_of_shards": shards,
            "number_of_replicas": replicas
        }

        index_spec['mappings']={
            "dynamic": "true",
            "_source": {
            "enabled": "true"
            },
            "properties": {},
        }
        
        for t in text_fields: 
            index_spec['mappings']['properties'][t]={
                    "type": "text"
                }

        for d in dense_fields: 
            index_spec['mappings']['properties'][d]={
                    "type": "dense_vector",
                    "dims": dense_fields_dim
                }

        with open(f'{folder}/spec_{index_name}.json', 'w') as index_file:
            json.dump(index_spec,index_file)


    def create_index(self, index_name, index_file=None):

        print(f"Creating the '{index_name}' index.")
        self.es.indices.delete(index=index_name, ignore=[404])

        if not index_file:
            source={
                "number_of_shards": 3,
                "number_of_replicas": 1
            }

        with open(index_file) as index_file:
            source = index_file.read().strip()
            self.es.indices.create(index=index_name, body=source)

    def write(self,index_name,docs,index_field=None):

        requests = []
        for i, doc in enumerate(docs):
            request = doc
            request["_op_type"] = "index"
            if index_field:
                request["_id"] = doc[index_field]
            request["_index"] = index_name
            requests.append(request)
        helpers.bulk(self.es, requests)

    def write_large_file(self, file_path, index_name, chunksize=10000, index_field='item_id'):
        """
        Assume file is csv
        """
        # read the large csv file with specified chunksize 
        df_chunk = pd.read_csv(file_path, chunksize=chunksize)

        chunk_list = []  # append each chunk df here 

        # Each chunk is in df format
        for chunk in tqdm.tqdm(df_chunk):  
            # perform data filtering 
            chunk_ls=json.loads(chunk.to_json(orient='records'))
            self.write(index_name,chunk_ls,index_field=index_field)

    def sample(self, index_name, size=3):
        return self.es.search(index=index_name, size=3)

    def search(self, index_name, field, query, type='match', size=10):
        res=[]
        res=self.es.search(index=index_name, body={'query':{type:{field:query}}},size=size)

        hits=res['hits']['hits']
        if len(hits)>0:
            keys=list(hits[0]['_source'].keys())

            out=[[h['_score']]+[h['_source'][k] for k in keys] for h in hits]

            df=pd.DataFrame(out,columns=['_score']+keys)
        else:
            df=pr.DataFrame([])
        logger.debug(f'Search {type.upper()} {query} in {index_name}.{field} returned {len(df)} results')
        return df