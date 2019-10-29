# db_config
## Setup an Instant S3-backed NoSQL HTTP Database

This NoSQL database protocol consists of a Node.js REST API Gateway, PyPy Worker API and your S3 Bucket as a storage back-end.

## Design Features

1. Using an S3 Bucket as a back-end provides a secure, cheap, highly-concurrent, always-available and maintenance-free option. You can also visualize/monitor your database from the AWS S3 Dashboard.

2. The PyPy Worker API localizes the database transaction cost (compute and network resources consumed) to the machine the database server is running on, allowing you to distribute network traffic/load over a cluster of servers efficiently while talking to the same storage backend concurrently. The worker API also utilizes the PyPy JIT compiler for extra performance.

3. The Node.js Gateway increases application-level database concurrency while also serving as an efficient queue.

Jump to [Performance](#Performance).

## Requirements

You need to have `Node`, `NPM`, `PyPy 2`, `Python 2.7+` and `Python Requests` installed for this service to work. You also need a working `S3 Bucket` with `programmatic access keys`.

### Command Line Setup

<pre><code>
$ sudo wget https://raw.githubusercontent.com/cmdimkpa/db_config/master/db_config.py
$ sudo python db_config.py import_config CONFIG_FILE_URL
$ sudo python db_config.py edit_config 		// make any required changes to config via interactive prompt)
$ sudo python db_config.py show_config 		// verify that config is accurate
$ sudo python db_config.py build_config 	// build the Database Server
$ sudo python db_config.py stop_config 		// stop the Database Server
</code></pre>

### CONFIG_FILE Structure

<pre><code>{
  "s3conn_user": S3_ACCESS_KEY_ID,
  "s3conn_pass": S3_SECRET_ACCESS_KEY,
  "s3region": S3_REGION,
  "s3bucket_name": DATABASE_S3_BUCKET_NAME,
  "server_host": DATABASE_SERVER_HOST,
  "server_port": DATABASE_SERVER_PORT
}</code></pre>

You can store your credentials online and expose a URL to `import_config` or just `edit_config` directly.

### Sample Database API Base URL

`http://server_host:server_port/ods/`

### Database Commands

#### 1. New Table

POST `.../ods/new_table`<br>
Payload:
<pre><code>
{
	"tablename":"Cars",
	"fields":["make","model","year"]
}
</code></pre>
Response:
<pre><code>
{
    "message": "prototype updated for object: CARS",
    "code": 201,
    "data": {}
}
</code></pre>

#### 2. New Record

POST `.../ods/new_record`<br>
Payload:
<pre><code>
{
  "tablename":"Cars",
  "data":{
      "make":"Ford",
      "model":"Focus",
      "year":2000
    }
}
</code></pre>
Response:
<pre><code>{
    "message": "logical table: Cars",
    "code": 200,
    "data": [
        {
            "Cars_id": "bd127d89f9f7b9780c05b87aec94b636",
            "__updated_at__": null,
            "model": "Corolla",
            "__created_at__": 1572276033,
            "year": 2010,
            "make": "Toyota",
            "row_id": 1,
            "__private__": 0
        }
    ]
}</code></pre>

#### 3. Fetch Records

POST `.../ods/fetch_records`<br>
Payload:
<pre><code>
{
  "tablename":"Cars",
  "constraints":{
      "make":"Toyota"
    }
}
</code></pre>
Response:
<pre><code>{
    "message": "logical table selection: Cars [1, 2]",
    "code": 200,
    "data": [
        {
            "Cars_id": "bd127d89f9f7b9780c05b87aec94b636",
            "__updated_at__": null,
            "__created_at__": 1572276033,
            "year": 2010,
            "row_id": 1,
            "model": "Corolla",
            "__private__": 0,
            "make": "Toyota"
        },
        {
            "Cars_id": "691fc731c81f874e161833b89e427815",
            "__updated_at__": null,
            "__created_at__": 1572276129,
            "year": 2008,
            "row_id": 2,
            "model": "Camry",
            "__private__": 0,
            "make": "Toyota"
        }
    ]
}
</code></pre>

#### 4. Update Records

POST `.../ods/update_records`<br>
Payload:
<pre><code>{
	"tablename":"Cars",
	"constraints":{
		"make":"Toyota"
		},
	"data":{
		"make":"Toyota Americas"
		}
}</code></pre>
Response:
<pre><code>{
    "message": "updated table selection: Cars [1, 2]",
    "code": 200,
    "data": [
        {
            "Cars_id": "bd127d89f9f7b9780c05b87aec94b636",
            "__updated_at__": 1572276538,
            "__created_at__": 1572276033,
            "year": 2010,
            "row_id": 1,
            "model": "Corolla",
            "__private__": 0,
            "make": "Toyota Americas"
        },
        {
            "Cars_id": "691fc731c81f874e161833b89e427815",
            "__updated_at__": 1572276538,
            "__created_at__": 1572276129,
            "year": 2008,
            "row_id": 2,
            "model": "Camry",
            "__private__": 0,
            "make": "Toyota Americas"
        }
    ]
}</code></pre>

#### 5. Delete Records

POST `.../ods/delete_records`<br>
Payload:
<pre><code>
{
	"tablename":"Cars",
	"constraints":{
		"model":"Corolla"
	}
}
</code></pre>
Response:
<pre><code>{
    "message": "deleted table selection: Cars [1]",
    "code": 200,
    "data": [
        {
            "Cars_id": "bd127d89f9f7b9780c05b87aec94b636",
            "__updated_at__": 1572277081,
            "__created_at__": 1572276033,
            "year": 2010,
            "row_id": 1,
            "model": "Corolla",
            "__private__": 1,
            "make": "Toyota Americas"
        }
    ]
}</code></pre>

#### 6. Database Stats

GET `.../ods/get_register`<br>
Response:
<pre><code>{
    "message": "Register Attached",
    "code": 200,
    "data": {
        "Cars": {
            "row_count": 4,
            "dataform": [
                "make",
                "model",
                "year",
                "row_id",
                "Cars_id",
                "private",
                "__created_at__",
                "__updated_at__",
                "__private__"
            ]
        }
    }
}</code></pre>

## Performance

A single node was tested in terms of concurrency and average response times under production-level traffic using a combination of `Apache Benchmark` and custom tests.

### Test Server Specs

`Ubuntu 18.04.2 LTS (GNU/Linux 4.15.0-1044-aws x86_64)`
`4GB RAM, 2 Cores`

### Apache Benchmark

`$ sudo ab -n 1000000 -c 100 http://X.X.X.X:X/ods/get_register`

This benchmark simulates 1 million concurrent requests from 100 connected applications against a single node. The operation performed is fetching the register.

The Image below shows the server load under the test:

![Server Load](https://kpmg-data-api.s3.us-east-2.amazonaws.com/server_test.png)

We can see that the load is well distributed over both available cores, and regardless of the heavy traffic, the single node is only at 70% capacity. It is also worthy of note that a single node can handle 1 million requests without breaking.

The results of the test are shown below:

<pre><code>
This is ApacheBench, Version 2.3 <$Revision: 1807734 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking X.X.X.X (be patient)
Completed 100000 requests
Completed 200000 requests
Completed 300000 requests
Completed 400000 requests
Completed 500000 requests
Completed 600000 requests
Completed 700000 requests
Completed 800000 requests
Completed 900000 requests
Completed 1000000 requests
Finished 1000000 requests


Server Software:
Server Hostname:        X.X.X.X
Server Port:            3066

Document Path:          /ods/get_register
Document Length:        627 bytes

Concurrency Level:      100
Time taken for tests:   1788.315 seconds
Complete requests:      1000000
Failed requests:        0
Total transferred:      969000000 bytes
HTML transferred:       627000000 bytes
Requests per second:    559.19 [#/sec] (mean)
Time per request:       178.831 [ms] (mean)
Time per request:       1.788 [ms] (mean, across all concurrent requests)
Transfer rate:          529.15 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       7
Processing:   127  179  23.1    173    1683
Waiting:      127  179  23.1    173    1683
Total:        127  179  23.1    173    1683

Percentage of the requests served within a certain time (ms)
  50%    173
  66%    180
  75%    186
  80%    191
  90%    209
  95%    223
  98%    239
  99%    253
 100%   1683 (longest request)

</code></pre>

<b>Single-node Concurrency (Production)</b>: 500 requests/second<br>
<b>Single-node Average Response Time (Production)</b>: 180ms

## Inquiries
Send questions/comments to: ayorinderay@gmail.com
