from intermix import intermix
import settings
import datetime
import time


def main():

    im = intermix(settings.API_TOKEN)

    CLUSTER_ID = settings.CLUSTER_ID

    users = im.get_users(CLUSTER_ID)

    current_time = datetime.datetime.now()

    params = {
      "startDate": (current_time - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S"),
      "endDate": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
      "resource": "query",
      "users": None,
      "dataPoints": 1,
      "conjunction": "and"
    }

    template_query_count_new =  "%(cluster_type)s/%(cluster_id)s/analytics"

    print "User Query Analytics for Cluster {0}\n".format(CLUSTER_ID)
    results = []
    for userobject in users:

        params["users"] = userobject["id"]
        data = im.api_request(cluster_id=CLUSTER_ID, template=template_query_count_new, params=params)
        time.sleep(0.1)  # API load

        serialized_data = {
            "id": userobject["id"],
            "username": userobject["username"],
            "count": data["data"][0]["count"],
            "avg_memory_MB": data["data"][0]["avg_memory"],
            "avg_rows": data["data"][0]["avg_rows"],
            "num_aborted": data["data"][0]["num_aborted"],
            "num_diskbased": data["data"][0]["num_diskbased"],
            "avg_queue_time_us": data["data"][0]["avg_queue_time"],
            "avg_exec_time_us": data["data"][0]["avg_exec_time"],
            "avg_duration_us": data["data"][0]["avg_duration"]
        }

        results.append(serialized_data)

    # header
    print "{}".format((",".join(list(results[0].keys()))))

    # rows
    for r in results:
        print "{}".format((",".join(map(str,r.values()))))

if __name__ == "__main__":

    main()