#!/usr/bin/env bash

now=$(date +"%Y_%m_%d")
tmp_dir_name="odg_backup_$now"
archive_name="$tmp_dir_name.tgz"
tmp_dir="/tmp/$tmp_dir_name"

if [ $# -ne 1 ]; then
    echo "Usage: $0 out_path"
    exit 1
else
    output_dir=$1
fi


function error_exit() {
    echo $1
    exit 1
}

function check_essential_containers_running() {
    containers=( "odg_neo4j" "odg_mongo" "odg_web" )
    for container in "${containers[@]}"; do 
        if [ ! "$(docker ps -q -f name=$container)" ]; then
            error_exit "Container $container is not running!!!"
        fi
    done
}

function create_temp_dir() {
    if [ -d $tmp_dir ]; then
        echo "Temp directory $tmp_dir already exists. Will remove..."
        remove_temp_dir
    fi
    mkdir $tmp_dir || error_exit "Couldn't create temp directory $tmp_dir!!!"
}

function remove_temp_dir() {
    echo "Removing temp directory $tmp_dir"
    rm -rf $tmp_dir
}

function backup_neo4j() {
    echo "Creating Neo4j backup..."
    cd $HOME && tar zcf $tmp_dir/neo4j.tar.gz neo4j && cd - || error_exit "Neo4j backup FAILED"
    echo "Neo4j backup SUCCESSFUL"
}

function backup_mongo() {
    echo "Creating mongoDB backup..."
    mongoDB_name=$(grep MONGODB_NAME .env | awk -F= '{ print $2 }')
    collections=( cache metadata pmid_cache pubmed_sentences )
    for collection in "${collections[@]}"; do 
        docker exec odg_mongo mongoexport --quiet --collection=$collection --db=$mongoDB_name --out=/tmp/$collection.json || error_exit "mongoexport for collection $collection FAILED"
        docker cp odg_mongo:/tmp/$collection.json $tmp_dir || error_exit "Copy of collection $collection FAILED"
        echo "Collection $collection exported"
    done
    echo "mongoDB backup SUCCESSFUL"
}

function backup_sqlite() {
    echo "Creating sqlite DB backup..."
    db_path=$(grep SQLITE_DB_PATH .env | awk -F= '{ print $2 }')
    docker cp odg_web:$db_path/app.db $tmp_dir || error_exit "Copy of sqlite DB FAILED"
    echo "mongoDB sqlite DB SUCCESSFUL"
}

function create_archive() {
    echo "Creating archive..."
    cd /tmp && tar zcf $output_dir/$archive_name $tmp_dir_name && cd - || error_exit "Archive creation FAILED"
    echo "Archive $output_dir/$archive_name creation SUCCESSFUL"
}

function backup() {
    echo ""
    backup_neo4j
    echo ""
    backup_mongo
    echo ""
    backup_sqlite
    echo ""
}

function main() {
    check_essential_containers_running
    create_temp_dir
    backup
    create_archive
    remove_temp_dir
    echo "Backup SUCCESSFUL"
    exit 0
}

main