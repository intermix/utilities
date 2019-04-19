#!/bin/bash
#
# new-intermix-user.sh 
#
# Copyright 2019, Intermix Software, Inc. All Rights Reserved
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

CLUSTER_ID=${1:-}
USERNAME=${2:-}
INTERMIX_USER=${3:-}
INTERMIX_PASS=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

if [ -z "$CLUSTER_ID" ] | [ -z "$USERNAME" ] | [ -z "$INTERMIX_USER" ]; then echo "$0 <cluster-id> <username> <intermix_user>"
    echo ""
    exit -1
fi

CLUSTER=$(aws redshift describe-clusters --cluster-identifier "$CLUSTER_ID" --query "Clusters[0].Endpoint")
CREDENTIALS=$(aws redshift get-cluster-credentials --cluster-identifier "$CLUSTER_ID" --db-user $USERNAME --db-name dev)


HOSTNAME=$(echo $CLUSTER | jq -r .Address)
PORT=$(echo $CLUSTER | jq -r .Port)

USERNAME=$(echo $CREDENTIALS | jq -r .DbUser)
PASSWORD=$(echo $CREDENTIALS | jq -r .DbPassword)

# WRITE temporary pgpassfile
TEMPFILE=$(mktemp)
chmod 600 ${TEMPFILE}

ESCAPED_USERNAME=$(echo $USERNAME | sed -e "s/:/\\\:/")
ESCAPED_PASSWORD=$(echo $PASSWORD | sed -e "s/:/\\\:/")

echo "$HOSTNAME:$PORT:dev:$ESCAPED_USERNAME:$ESCAPED_PASSWORD" > ${TEMPFILE}
echo "CREATE USER ${INTERMIX_USER} PASSWORD '${INTERMIX_PASS}' SYSLOG ACCESS UNRESTRICTED;" > intermix_grant_generated.sql
echo "GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog to ${INTERMIX_USER};" >> intermix_grant_generated.sql

PGPASSFILE=${TEMPFILE} psql -h $HOSTNAME -p $PORT -U ${USERNAME} dev -f intermix_grant_generated.sql

echo
echo
echo "Intermix User Credentials: "
echo "    username: ${INTERMIX_USER}"
echo "    password: ${INTERMIX_PASS}"
    
rm intermix_grant.sql
rm ${TEMPFILE}