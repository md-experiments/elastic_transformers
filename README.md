# ElasticTransformers
Semantic Elasticsearch with Sentence Transformers. We will use the power of Elasti and the magic of BERT to idnex a million articles and perform lexical and semantic search on them. The main contribution here is the ease of use to create your own local search engine

This repo combines together the following amazing works by brilliant people

### The ML part
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers)  
- [transformers](https://github.com/huggingface/transformers)  
- [BERT](https://github.com/google-research/bert)
### The engineering part
- [Elasticsearch](https://www.elastic.co/home)  
- [Docker](https://hub.docker.com)

## Overview
We will use the above to 
- Set up an Elasticsearch server with Dockers
- Collect A Million News Headlines
- Use sentence-transformers to index them onto Elastic (takes about 6 hrs on 2 CPU cores)
- Look at some comparison examples between lexical and semantic search

## Setup
### Set up your environment
Mine environment is called `et` and I use conda for this. Navigate inside the project directory
```
conda create --name et python=3.7  
conda install -n et nb_conda_kernels  
pip install -r requirements.txt
```

### Get the data
For this tutorial I am using [A Million News Headlines](https://www.kaggle.com/therohk/million-headlines "Kaggle A Million News Headlines") by Rohk and place it in the data folder inside the project dir.   
You will find that the steps are otherwise pretty abstracted so you can also do this with your dataset of choice

### Elasticsearch with Docker
Follow the instructions on setting up Elastic with Docker from Elastic's page [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
For this tutorial, you only need to run the two steps:
 - [Pulling the image](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_pulling_the_image)
 - [Starting a single node cluster with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-dev-mode)

## Usage

After successful setup, use the folling notebooks to make this all work
- [Setting up the index](../notebooks/Setting up ElasticTransformers.ipynb)
- [Searching](../notebooks/Searching with ElasticTransformers.ipynb)