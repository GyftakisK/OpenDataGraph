# Open Data Graph
## Dependencies
 * [Docker Compose](https://docs.docker.com/compose/install/) 
 * Local installation of [SemRep v1.7](https://semrep.nlm.nih.gov/SemRep.v1.7_Installation.html), which also requires local installation of [Metamap](https://metamap.nlm.nih.gov/Installation.shtml)
 * Active account to [UMLS Terminology Services](https://uts.nlm.nih.gov/uts/)
 
 ## Configuration
 
 ### .env file
 Configure the following environmental variables before execution.

 #### Mail server options
 An mail server should be configured in order to facilitate user password reset and crash reporting for administrators, using the following environmental variables:

  1. __MAIL_SERVER__: IP address of the mail server
  2. __MAIL_PORT__: Port number of the mail server
  3. __MAIL_USE_TLS__: 1 to use TLS, remove if not needed
  4. __MAIL_USERNAME__: Username to be used for access to mail server
  5. __MAIL_PASSWORD__: Password to be used for access to mail server
 
 #### SemRep, Metamap and UMLS API
 
 1. __UMLS_API_KEY__: Add your API key from your UTS profile [See Step 1](https://documentation.uts.nlm.nih.gov/rest/authentication.html)
 2. __SEMREP_DIR__: Full path to directory that contains SemRep local installation (make sure non-root users have access) 
 3. __METAMAP_DIR__: Full path to directory that contains MetaMap local installation (make sure non-root users have access)
 
 #### Optional configuration
 Change the following values only if needed. Default values work with the provided __docker-compose.yml__.

  1. __SQLITE_DB_PATH__: Path to directory containing SQLITE DB file
  2. __MONGODB_HOST__: Hostname or IP address of mongoDB instance
  3. __MONGODB_PORT__: Port number of mongoDB instance
  4. __MONGODB_NAME__: Name of the DB used for cache and intermediate data
  5. __UPLOAD_FOLDER__: Directory where uploaded files are saved
  6. __NEO4J_HOST__: Hostname or IP address of Neo4j instance
  7. __NEO4J_PORT__: Port number of Neo4j instance
  8. __NEO4J_USER__: Username used for authentication in Neo4j instance
  9. __NEO4J_PASS__: Password used for authentication in Neo4j instance
  10. __GUNICORN_OPTIONS__: Keyword options passed to gunicorn. Reference [here](https://docs.gunicorn.org/en/stable/settings.html)

### config.py

* __ADMINS__ = Add here admin users that will be auto-created during deployment (Default password: **admin**)

### dockerfile.celery_job_worker
Change INVALID_UID to a user ID that has access to __SEMREP_DIR__ and __METAMAP_DIR__.  

## Deployment

You can deploy the system using [Docker Compose](https://docs.docker.com/compose/gettingstarted/#step-4-build-and-run-your-app-with-compose) and the provided __docker-compose.yml__, by running:
```bash
docker-compose up
```
Upon successful build and deployment, Web aplication should be accessible on port 5000.  
