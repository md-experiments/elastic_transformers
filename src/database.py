from elasticsearch import Elasticsearch, helpers
import datetime
import json
import pandas as pd
import tqdm
import os
from src.logger import logger

class ElasticTransformers(object):
    def __init__(self,url='http://localhost:9200', index_name=None):
        """
        Initializes class

        Args:
            url (string) full url for elastic
            index_name (string, optional) name of index can be used as the default index across all methods for this class instance should this apply
        """
        self.url=url
        self.es=Elasticsearch(self.url)
        self.index_name=index_name
        self.index_file=None

    def ping(self):
        """
        Checks if Elastic is healthy

        Returns:
            True if healthy, False otherwise
        """
        ping=self.es.ping()
        if ping:
            logger.debug(f'Ping successful')
        return ping

    def create_index_spec(self, index_name=None,folder='index_spec',text_fields=[], keyword_fields=[], dense_fields=[], dense_fields_dim=512, shards=3, replicas=1):
        """
        Creates mapping file for an index and stores the file

        Args:
            index_name (string, optional) name of index, defaults to index name defined when initiating the class
            folder (string) location to store index spec
            text_fields (list)
            keyword_fields (list)
            dense_fields (list) list of dense field names
            dense_fields_dim (int) 
            shards (int) number of shards for index
            replicas (int) number of replicas for index
        """
        
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
        logger.debug(f'Index spec {self.index_file} created')
        return index_spec

    def create_index(self, index_name=None, index_file=None):
        """
        Create index (index_name) based on file (index_file) containing index mapping
        NOTE: existing index of this name will be deleted
        
        Args:
            index_name (string, optional): name of index, defaults to index name defined when initiating the class
            index_file (string, optional): index spec file location, if none provided, will use mapping from create_index_spec else will create blank mapping
        
        """
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
            docs (list) list of dictionaries with keys matching index field names from index specification
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

        Args:
            file_path (string) path to file
            index_name (string, optional) name of index, defaults to index name defined when initiating the class
            chunksize (int) size of the chunk to be read from file and sent to embedder
            embedder (function) embedder function with expected call embedded(list of strings to embed)
            field_to_embed (string) name of field to embed
            index_field (string, optional) name of index field if present in docs. Defaults to elasicsearch indexing otherwise
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
            if embedder:
                chunk[f'{field_to_embed}_embedding']=embedder(chunk[field_to_embed].values)
            chunk_ls=json.loads(chunk.to_json(orient='records'))
            self.write(chunk_ls,index_name,index_field=index_field)
            logger.debug(f'Successfully wrote {len(chunk_ls)} docs to {index_name}')

    def sample(self, index_name=None, size=3):
        """
        Provides a sample of documents from the index

        Args:
            index_name (string, optional) name of index, defaults to index name defined when initiating the class
            size (int, optional) number of results to retrieve, defaults to 3, max 10k, can be relaxed with elastic config             
        """
        if not index_name:
            if self.index_name:
                index_name=self.index_name
            else:
                raise ValueError('index_name not provided')
        res=self.es.search(index=index_name, size=size)
        logger.debug(f"Successfully sampled {len(res['hits']['hits'])} docs from {index_name}")
        return res

    def search(self, query, field, type='match', index_name=None, embedder=None, size=10):
        """
        Search elastic

        Args:
            query (string) search query
            field (string) field to search
            type (string) type of search, takes: match, term, fuzzy, wildcard (requires "*" in query), dense (semantic search, requires embedder, index needs to be indexed with embeddings, assumes embedding field is named {field}_embedding)
            index_name (string, optional) name of index, defaults to index name defined when initiating the class
            embedder (function) embedder function with expected call embedded(list of strings to embed)
            size (int, optional) number of results to retrieve, defaults to 3, max 10k, can be relaxed with elastic config

        Returns:
            DataFrame with results and search score
        """
        res=[]
        if type=='dense':
            if not embedder:
                raise ValueError('Dense search requires embedder')
            query_vector = embedder([query])[0]

            script_query = {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, doc['{field}_embedding']) + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }

            res = self.es.search(
                index=index_name,
                body={
                    "size": size,
                    "query": script_query,
                    "_source": {"excludes": [f'{field}_embedding']}
                }
            )
        else:
            res=self.es.search(index=index_name, body={'query':{type:{field:query}}, "_source": {"excludes": [f'{field}_embedding']}},size=size)
        self.search_raw_result=res
        hits=res['hits']['hits']
        if len(hits)>0:
            keys=list(hits[0]['_source'].keys())

            out=[[h['_score']]+[h['_source'][k] for k in keys] for h in hits]

            df=pd.DataFrame(out,columns=['_score']+keys)
        else:
            df=pd.DataFrame([])
        self.search_df_result=df
        logger.debug(f'Search {type.upper()} {query} in {index_name}.{field} returned {len(df)} results of {size} requested')
        return df