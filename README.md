# db_config
## Setup an Instant S3-backed NoSQL HTTP Database

### Requirements

You need to have `Node`, `NPM`, `Python2.7+` and `Python Requests` installed for this to work. You also need a working `S3 Bucket` with `programmatic access keys`.

### Command Line Setup

`$ sudo wget https://raw.githubusercontent.com/cmdimkpa/db_config/master/db_config.py`<br>
`$ sudo db_config.py import_config <CONFIG_FILE_URL>`<br>
`$ sudo db_config.py edit_config`<br>
`$ sudo db_config.py show_config`<br>
`$ sudo db_config.py build_config` (to start Database Server)<br>

## CONFIG_FILE Structure

`{`<br>
  ` "s3conn_user":<S3_ACCESS_KEY_ID>,`<br>
  ` "s3conn_pass":<S3_SECRET_ACCESS_KEY>,`<br>
  ` "s3region":<S3_REGION>,`<br>
  ` "s3bucket_name":<DATABASE_S3_BUCKET_NAME>,`<br>
  ` "server_host":<DATABASE_SERVER_HOST>,`<br>
  ` "server_port":<DATABASE_SERVER_PORT>`<br>
`}`

You can store your credentials online and expose a URL to `import_config` or just `edit_config` directly.

## Sample Database API Base URL

`http://<server_host:server_port>/ods/`

## Database Commands

### 1. New Prototype (data model)

POST `.../ods/new_prototype`<br>
Payload: `{
  "object":"Cars",
  "dataform":{
      "make":null,
      "model":null,
      "year":null
    }
}`<br>
Response:`{
    "message": "prototype updated for object: CARS",
    "code": 201,
    "data": {}
}`

### 2. New Record

POST `.../ods/new_record`<br>
Payload: `{
  "tablename":"Cars",
  "data":{
      "make":"Ford",
      "model":"Focus",
      "year":2000
    }
}`<br>
Response:`{
    "message": "logical table: Cars",
    "code": 200,
    "data": [
        {
            "Cars_id": "a16240d4db9cd0e489ebd4ba648b8dbd",
            "model": "Focus",
            "year": 2000,
            "row_id": 1,
            "make": "Ford"
        }
    ]
}`

### 3. Fetch Record

POST `.../ods/fetch_record`<br>
Payload: `{
  "tablename":"Cars",
  "constraints":{
      "make":"Toyota"
    }
}`<br>
Response:``{
    "message": "logical table selection: Cars [3, 4]",
    "code": 200,
    "data": {
        "data": {
            "data": {
                "Cars": [
                    {
                        "Cars_id": "41e27a59f9e9f0bc309d278eb0d9c504",
                        "make": "Toyota",
                        "model": "Camry",
                        "row_id": 3,
                        "year": 2007
                    },
                    {
                        "Cars_id": "b2c98f37bdadc7fea478a457fd62f8d2",
                        "model": "Corolla",
                        "year": 2010,
                        "row_id": 4,
                        "make": "Toyota"
                    }
                ]
            }
        }
    }
}``

### 4. Update Record

POST `.../ods/update_record`<br>
Payload: `{
  "tablename":"Cars",
  "constraints":{
      "make":"Toyota"
    },
  "data":{
    "make":"Toyota Europe"
  }
}`<br>
Response:``{
    "message": "logical table selection: Cars [3, 4]",
    "code": 200,
    "data": {
        "data": {
            "data": {
                "Cars": [
                    {
                        "Cars_id": "41e27a59f9e9f0bc309d278eb0d9c504",
                        "make": "Toyota",
                        "model": "Camry",
                        "row_id": 3,
                        "year": 2007
                    },
                    {
                        "Cars_id": "b2c98f37bdadc7fea478a457fd62f8d2",
                        "model": "Corolla",
                        "year": 2010,
                        "row_id": 4,
                        "make": "Toyota"
                    }
                ]
            }
        }
    }
}``
