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
        "PhoneBookZ": {
            "row_count": 0,
            "dataform": [
                "first_nameZ",
                "phone_numberZ",
                "emailZ",
                "last_nameZ",
                "row_id",
                "PhoneBookZ_id"
            ]
        },
        "PhoneBook": {
            "row_count": 3,
            "dataform": [
                "phone_number",
                "first_name",
                "last_name",
                "email",
                "row_id",
                "PhoneBook_id"
            ]
        },
        "FRMJobRequest": {
            "row_count": 3,
            "dataform": [
                "template_name",
                "b64_csv_1",
                "job_processed",
                "b64_csv_2",
                "owner_token",
                "engagement_id",
                "job_output_urls",
                "template_url",
                "parameter_dict",
                "row_id",
                "FRMJobRequest_id"
            ]
        },
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


## Inquiries
Send questions/comments to: ayorinderay@gmail.com
