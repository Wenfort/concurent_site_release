import io
import xlsxwriter


def export_page(request_list, user_role):

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()

    if request_list:
        worksheet.set_column(0, 0, 50)
        if user_role == 'admin':
            worksheet.set_column(1, 9, 15)
            worksheet_headers = ['Текст запроса',
                                 'Сложность от возраста',
                                 'Сложность от стема',
                                 'Сложность от объема',
                                 'Сложность от ссылочного',
                                 'Конкуренция SEO',
                                 'Эффект директа',
                                 'Итоговая сложность',
                                 'Гео',
                                 'Запросов в месяц'
            ]
            worksheet.write_row(0, 0, worksheet_headers)
            row = 1
            for request in request_list:
                values = [request.request_text,
                          request.site_age_concurency,
                          request.site_stem_concurency,
                          request.site_volume_concurency,
                          request.site_backlinks_concurency,
                          request.site_seo_concurency,
                          request.direct_upscale,
                          request.site_total_concurency,
                          request.region_id,
                          request.request_views,
                ]
                worksheet.write_row(row, 0, values)

                row += 1
        else:
            worksheet.set_column(1, 9, 15)
            worksheet_headers = ['Текст запроса',
                                 'Конкуренция SEO',
                                 'Конкуренция Direct',
                                 'Итоговая сложность',
                                 'Гео',
                                 'Запросов в месяц',
                                 ]
            worksheet.write_row(0, 0, worksheet_headers)
            row = 1

            for request in request_list:
                values = [request.request_text,
                          request.site_seo_concurency,
                          request.direct_upscale,
                          request.site_total_concurency,
                          request.region_id,
                          request.request_views,
                ]
                worksheet.write_row(row, 0, values)

                row += 1

    workbook.close()
    buffer.seek(0)

    return buffer