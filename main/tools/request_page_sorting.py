def unmask_sort_type(masked_sort_type):
    """Прячет от пользователя реальное название row в таблице БД"""
    unmasked_sort_type = str()
    if 'request' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('request', 'request_text')
    elif 'age' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('age', 'age_concurency')
    elif 'stem' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('stem', 'stem_concurency')
    elif 'volume' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('volume', 'volume_concurency')
    elif 'backlinks' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('backlinks', 'backlinks_concurency')
    elif 'seo' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('seo', 'seo_concurency')
    elif 'direct' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('direct', 'direct_upscale')
    elif 'total' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('total', 'total_concurency')
    elif 'region' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('region', 'region_id')
    elif 'amount' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('amount', 'request_views')
    elif 'vital_count' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('vital_count', 'vital_sites_count')
    elif 'avg_backs' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_backs', 'average_total_backlinks')
    elif 'avg_unique_backs' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_unique_backs', 'average_unique_backlinks')
    elif 'avg_vol' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_vol', 'average_volume')
    elif 'avg_old' in masked_sort_type:
        unmasked_sort_type = masked_sort_type.replace('avg_old', 'average_age')

    return unmasked_sort_type