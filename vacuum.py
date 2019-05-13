from intermix import intermix
import settings
import argparse

def construct_cmd_string(schema_name="", table_name="", type="", val="",row_count="",sort_key=""):

    if type == "ANALYZE":
        executables = ["vacuum delete only", "analyze"]
    elif type == "SORT" and sort_key != "INTERLEAVED":
        executables = ["vacuum sort only"]
    elif type == "SORT" and sort_key == "INTERLEAVED":
        executables = ["vacuum reindex"]

    out = []
    for e in executables:
        out.append("{} {}.{} /* value:{} rows:{} */".format(e, schema_name, table_name, val, row_count))
    return out

def gen_script(data="",filename="",username="",host="",port=""):

    header = """
#!/bin/bash
# Intermix.io Vacuum Script
#
# This script requires the psql postgres command line client be installed prior
# to running.  The psql client is avaliable for download here,
# https://www.postgresql.org/download/.
#
#
# You will be prompted for the administrator password


# Override the administrator username here
adminuser="{}"

psqlcommand="psql -e"

# Don't edit anything beyond this point
logindb="dev"
redshiftport="{}"
redshifthost="{}"

${{psqlcommand}} -d ${{logindb}} -U ${{adminuser}} -p ${{redshiftport}} -h ${{redshifthost}} <<EOF

""".format(username, port, host)

    if filename:
        f = open(filename, 'w')
        f.write(header)
        for db,cmds in data.iteritems():
            f.write("\n\c {}\n".format(db))
            for cmd in cmds:
                f.write("{};\n".format(cmd))
        f.close()
    else:
        print "{}\n".format(header)
        for db, cmds in data.iteritems():
            print "\n\c {}\n".format(db)
            for cmd in cmds:
                print "{};".format(cmd)


def main():

    im = intermix(settings.API_TOKEN)

    CLUSTER_ID = settings.CLUSTER_ID
    USERNAME = settings.VACUUM_REDSHIFT_USERNAME
    REDSHIFT_HOST = settings.VACUUM_REDSHIFT_HOST
    REDSHIFT_PORT = settings.VACUUM_REDSHIFT_PORT

    template_table_info = "%(cluster_type)s/%(cluster_id)s/tables"

    params = {
        "fields": "table_id,table_name,schema_id,schema_name,db_id,db_name,stats_pct_off,size_pct_unsorted,row_count,sort_key"
        }

    data = im.api_request(cluster_id=CLUSTER_ID, template=template_table_info, params=params)

    cmds_to_run = {}

    parser = argparse.ArgumentParser(description='Build Vacuum script')
    parser.add_argument('-o', '--output', type=str, required=True, help='Enter a filename or "STDOUT" to send to standard out')
    parser.add_argument('-t', '--type', type=str, required=True, help='Enter SORT to output a script for sorting tables, or ANALYZE for a script to vacuum delete and analyze tables.')

    options = parser.parse_args()

    if options.output == "STDOUT":
        OUTPUT_FILENAME = None
    else:
        OUTPUT_FILENAME = options.output

    if options.type == "ANALYZE":
        metric = "stats_pct_off"
        threshold = 10
    elif options.type == "SORT":
        metric = "size_pct_unsorted"
        threshold = 10
    else:
        print "Type should be one of 'SORT' or 'ANALYZE', exiting..."
        exit(0)

    for d in sorted(data["data"], key=lambda foo: foo[metric], reverse=True):
        val = d[metric]
        schema_name = d["schema_name"]
        table_name = d["table_name"]
        db_name = d["db_name"]
        row_count = d["row_count"]
        sort_key = d["sort_key"]

        if not schema_name == "pg_internal" and (val > threshold):
            try:
                cmds_to_run[db_name] += construct_cmd_string(schema_name,table_name,type=options.type,
                                                            val=val,row_count=row_count,sort_key=sort_key)
            except:
                cmds_to_run[db_name] = construct_cmd_string(schema_name, table_name,type=options.type,
                                                            val=val, row_count=row_count,sort_key=sort_key)

    gen_script(data=cmds_to_run, filename=OUTPUT_FILENAME, username=USERNAME,
                host=REDSHIFT_HOST, port=REDSHIFT_PORT)


if __name__ == "__main__":

    main()