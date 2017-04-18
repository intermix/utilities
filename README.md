# Intermix API Utilities

Copyright 2017 Intermix Software, Inc. All Rights Reserved.

Licensed under the MIT License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

https://opensource.org/licenses/MIT

Intermix is an analytics platform that instruments Amazon Redshift to improve performance, reduce costs, and eliminate downtime.
Our SaaS product intelligently tunes databases in the cloud, provides deep analytics, recommendations, and predictions, so companies don't have
to hire DBA experts, throw money at performance problems, or deal with slow queries.


## Getting Started

These instructions will help set up your environment to execute these scripts locally.


### Prerequisites

The following are required to create a local development instance.

+ Python 2.7.6+ (Python 2.7.12 is recommended)
+ PIP Package manager for Python

To install the prerequisites:

```
pip install -r ./requirements.txt
```

### Configuration Settings

The file `settings_local.py` contains sensitive data for your environment. 
Simply rename the file `settings_local.py.default` and edit the file accordingly.


## Utilities

### Vacuum

The following utility will generate a bash script that can be executed to reclaim deleted space and update row statistics on all tables in your cluster.
Only tables that have space to be reclaimed will be touched.

The utility will first call the Intermix API to retrieve a list of tables whos statistics are > 10% stale,
and then generate the script and include all necessary information to log into your Redshift cluster. When you run the script, you
will be prompted for your user password.

Note: You must first create a `settings_local.py` file and enter information that will be used to generate the script.

This utility will **not** access your cluster, it will simply generate a bash script.
 
#### Usage

```
vacuum.py

Generates a script to execute 'vacuum delete only' and 'analyze' on tables that require it.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Enter a filename or "STDOUT"
```



#### Example

```
python ./vacuum.py -o foo.sh
```

Then execute the bash script with

```
bash ./foo.sh
```


### User Analytics

Will outpu a CSV to STDOUT that contains user statistics for the past 7 days.
 
#### Usage

```
user_analytics.py

Generates a CSV for per-user statistics including query counts, latency, memory usage, and more.

<no optional arguments>

```



#### Example

```
python ./user_analytics.py
```

