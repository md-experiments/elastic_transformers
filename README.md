# ElasticTransformers
Semantic Elasticsearch with Sentence Transformers. We will use the power of Elastic and the magic of BERT to idnex a million articles and perform lexical and semantic search on them.  

The purpose is to provide an ease-of-use way of setting up your own Elasticsearch with near state of the art capabilities of contextual embeddings / semantic search using NLP transformers.  

## Overview
We will use the above to 
- Set up an Elasticsearch server with Dockers
- Collect A Million News Headlines
- Use sentence-transformers to index them onto Elastic (takes about 6 hrs on 2 CPU cores)
- Look at some comparison examples between lexical and semantic search

## Setup
### Set up your environment
My environment is called `et` and I use conda for this. Navigate inside the project directory
```
conda create --name et python=3.7  
conda install -n et nb_conda_kernels  
pip install -r requirements.txt
```

### Get the data
For this tutorial I am using [A Million News Headlines](https://www.kaggle.com/therohk/million-headlines "Kaggle A Million News Headlines") by Rohk and place it in the data folder inside the project dir.   

	    elastic_transformers/
	    ├── data/

You will find that the steps are otherwise pretty abstracted so you can also do this with your dataset of choice

### Elasticsearch with Docker
Follow the instructions on setting up Elastic with Docker from Elastic's page [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
For this tutorial, you only need to run the two steps:
 - [Pulling the image](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_pulling_the_image)
 - [Starting a single node cluster with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-dev-mode)

## Usage
After successful setup, use the folling notebooks to make this all work  
- [Setting up the index](../master/notebooks/Setting_up_ElasticTransformers.ipynb)
- [Searching](../master/notebooks/Searching_with_ElasticTransformers.ipynb)

## References
This repo combines together the following amazing works by brilliant people. Please check out their work if you haven't done so yet...

### The ML part
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers)  
- [transformers](https://github.com/huggingface/transformers)  
- [BERT](https://github.com/google-research/bert)
### The engineering part
- [Elasticsearch](https://www.elastic.co/home)  
- [Docker](https://hub.docker.com)
