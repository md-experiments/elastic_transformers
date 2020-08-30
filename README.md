# ElasticTransformers
Semantic Elasticsearch with Sentence Transformers. This repo combines together the following amazing works by brilliant people

[sentence-transformers](https://github.com/UKPLab/sentence-transformers)
[transformers](https://github.com/huggingface/transformers)
[Elasticsearch](https://www.elastic.co/home)

## Setup
### Set up your environment
Mine environment is called et and I use conda for this. Navigate inside the project directory
```
conda create --name et python=3.7  
conda install -n et nb_conda_kernels  
pip install -r requirements.txt
```

### Get the data
For this tutorial I am using [A Million News Headlines dataset by Rohk](https://www.kaggle.com/therohk/million-headlines "Kaggle A Million News Headlines") and place it in the data folder inside the project dir.   
You will find that the steps are otherwise pretty abstracted so you can also do this with your dataset of choice

### Elasticsearch with Docker
Follow the instructions on setting up Elastic with Docker from Elastic's page [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
For this tutorial, you only need to run the two steps:
 - [Pulling the image](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_pulling_the_image)
 - [Starting a single node cluster with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-dev-mode)
