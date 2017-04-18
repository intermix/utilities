from intermix import intermix
import settings
import argparse

def construct_cmd_string(schema_name="", table_name=""):

	executables = ["vacuum delete only", "analyze"]
	out = []
	for e in executables:
		out.append("{} {}.{}".format(e, schema_name, table_name))
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

	CLUSTER_ID = settings.VACUUM_CLUSTER_ID
	USERNAME = settings.VACUUM_REDSHIFT_USERNAME
	REDSHIFT_HOST = settings.VACUUM_REDSHIFT_HOST
	REDSHIFT_PORT = settings.VACUUM_REDSHIFT_PORT

	template_table_info = "%(cluster_type)s/%(cluster_id)s/tables"

	params = {
		"fields": "table_id,table_name,schema_id,schema_name,db_id,db_name,stats_pct_off"
		}

	data = im.api_request(cluster_id=CLUSTER_ID, template=template_table_info, params=params)

	cmds_to_run = {}

	parser = argparse.ArgumentParser(description='Build Vacuum script')
	parser.add_argument('-o', '--output', type=str, required=True, help='Enter a filename or "STDOUT"')

	options = parser.parse_args()

	if options.output == "STDOUT":
		OUTPUT_FILENAME = None
	else:
		OUTPUT_FILENAME = options.output

	for d in data["data"]:

		stats_off_pct = d["stats_pct_off"]
		schema_name = d["schema_name"]
		table_name = d["table_name"]
		db_name = d["db_name"]

		if not schema_name == "pg_internal" and (stats_off_pct > 10):

			try:
				cmds_to_run[db_name] += construct_cmd_string(schema_name,table_name)
			except:
				cmds_to_run[db_name] = construct_cmd_string(schema_name, table_name)

	gen_script(data=cmds_to_run, filename=OUTPUT_FILENAME, username=USERNAME,
				host=REDSHIFT_HOST, port=REDSHIFT_PORT)


if __name__ == "__main__":

    main()