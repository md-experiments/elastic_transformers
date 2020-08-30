from elasticsearch import Elasticsearch, helpers
import datetime
import json
import pandas as pd
import tqdm
import os
from src.logger import logger

class ElasticSearchClass(object):
    def __init__(self,url='http://localhost:9200', index_name=None):
        self.url=url
        self.es=Elasticsearch(self.url)
        self.index_name=index_name
        self.index_file=None

    def ping(self):
        return self.es.ping()

    def create_index_spec(self, index_name=None,folder='index_spec',text_fields=[], keyword_fields=[], dense_fields=[], dense_fields_dim=512, shards=3, replicas=1):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if not index_name:
            if self.index_name:
                index_name=self.index_name
            else:
                raise ValueError('index_name not provided') 
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

        for k in keyword_fields: 
            index_spec['mappings']['properties'][t]={
                    "type": "keyword"
                }

        for d in dense_fields: 
            index_spec['mappings']['properties'][d]={
                    "type": "dense_vector",
                    "dims": dense_fields_dim
                }

        index_file_name=f'{folder}/spec_{index_name}.json'
        with open(index_file_name, 'w') as index_file:
            json.dump(index_spec,index_file)
        self.index_file=index_file_name
        return index_spec

    def create_index(self, index_name=None, index_file=None):

        if not index_name:
            if self.index_name:
                index_name=self.index_name
            else:
                raise ValueError('index_name not provided') 
        print(f"Creating '{index_name}' index.")
        self.es.indices.delete(index=index_name, ignore=[404])
        
        if index_file or self.index_file:
            if self.index_file:
                index_file=self.index_file
            with open(index_file) as index_file:
                index_spec = index_file.read().strip()
                
        else:
            index_spec={
                "number_of_shards": 3,
                "number_of_replicas": 1
            }

        self.es.indices.create(index=index_name, body=index_spec)

    def write(self,docs,index_name=None,index_field=None):
        """
        Writes entries to index

        Args:
            docs (iterable) iterable with keys matching index field names from index specification
            index_name (string, optional) name of index, defaults to index name defined when initiating the class
            index_field (string, optional) name of index field if present in docs. Defaults to elasicsearch indexing otherwise
        
        """
        if not index_name:
            if self.index_name:
                index_name=self.index_name
            else:
                raise ValueError('index_name not provided')
        requests = []
        for i, doc in enumerate(docs):
            request = doc
            request["_op_type"] = "index"
            if index_field:
                request["_id"] = doc[index_field]
            request["_index"] = index_name
            requests.append(request)
        helpers.bulk(self.es, requests)

    def write_large_csv(self, file_path, index_name=None, chunksize=10000, embedder=None, field_to_embed=None, index_field=None):
        """
        Iteratively reads through a csv file and writes it to elastic in batches


        """
        if not index_name:
            if self.index_name:
                index_name=self.index_name
            else:
                raise ValueError('index_name not provided')
        # read the large csv file with specified chunksize 
        df_chunk = pd.read_csv(file_path, chunksize=chunksize, index_col=0)

        chunk_list = []  # append each chunk df here 

        # Each chunk is in df format
        for chunk in tqdm.tqdm(df_chunk): 
            chunk[f'{field_to_embed}_embedding']=embedder(chunk[field_to_embed].values)
            chunk_ls=json.loads(chunk.to_json(orient='records'))
            self.write(chunk_ls,index_name,index_field=index_field)

    def sample(self, index_name=None, size=3):
        if not index_name:
            if self.index_name:
                index_name=self.index_name
            else:
                raise ValueError('index_name not provided')
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