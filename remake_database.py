import postgres_mode as pm

pm.custom_request_to_database_without_return(f"UPDATE concurent_site.main_domain "
                                          f"SET domain_group = 1 "
                                          f"WHERE unique_backlinks >= 10000;")