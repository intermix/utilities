\c dev

CREATE USER intermix PASSWORD << CHANGEME >> SYSLOG ACCESS UNRESTRICTED;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog to intermix;