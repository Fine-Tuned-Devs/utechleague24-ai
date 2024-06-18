# UTechLeague 2024 - AI Backend

## Development

1. Copy `example.env` into another file called `.env` and fill all values

2. Run:
    ```shell
   docker build -t my_fastapi_app .
   docker run -d -p 8080:8080 --name fastapi_container my_fastapi_app
   ```