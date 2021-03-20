from postgres_mode import custom_request_to_database_without_return

custom_request_to_database_without_return('UPDATE concurent_site.main_domain SET domain_group = 1 '
                                          'WHERE unique_backlinks > 10000;')