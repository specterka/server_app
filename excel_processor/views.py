# views.py
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadExcelForm
from django.http import JsonResponse
import json
from django.shortcuts import render
from django.urls import reverse
from django.http import FileResponse
import os
import logging

logger = logging.getLogger(__name__)

def homepage(request):
    return render(request, 'homepage.html')

def calculate_discount(row):
    categories = ['Холодильники', 'Струбцины', 'Топоры','Строительные материалы','Строительное оборудование','Средства индивидуальной защиты','Отделочные материалы'
                  'Окна и двери','Напольные покрытия','Ручные инструменты','Системы отопления и вентиляции','Измерительные инструменты','Строительные смеси',
                  'Лакокрасочные материалы','Сантехника','Инструменты','Кровельные материалы','Оснастка для инструмента','Автокомпрессоры','Автомобильное освещение',
                  'Ванная комната','Балдахины и опоры для кроваток','Кресла и стулья','Прихожая','Кухня','Гостиная','Детские матрасы',
                  'Офис','Столы','Туризм и отдых на природе','Велоспорт','Товары для рыбалки','Товары для охоты','Зимний спорт',
                  'Аксессуары для ванной','Инвентарь для уборки','Решетки для гриля','Грили и коптильни','Мангалы','Отдых и пикник','Садовая техника',
                  'Садовая мебель','Шампуры','Тандыры',]
    if row['Категория'] in categories:
        return 0.11 * row['Сумма']
    else:
        return 0.12 * row['Сумма']

def calculate_result(row):
    summa = row['Сумма']
    discount = calculate_discount(row)
    price = row['Закуп']
    weight = row['Доставка']

    if summa < 5000:
        return summa - discount - price
    elif 5000 <= summa < 15000:
        return summa - discount - price - 800
    else:
        return summa - discount - price - weight

def merge_data(request):
    context = {}
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            user_excel_file = request.FILES['excel_file']
            df_user = pd.read_excel(user_excel_file)

            df_database = pd.read_excel('database.xlsx')

            # Merge the data using VLOOKUP-like functionality
            df_merged = df_user.merge(df_database, how='left', left_on='Артикул', right_on='Артикул')
            df_merged.fillna('', inplace=True)

            # Calculate the result
            df_merged['Сумма'] = pd.to_numeric(df_merged['Сумма'], errors='coerce')
            df_merged['Закуп'] = pd.to_numeric(df_merged['Закуп'], errors='coerce')
            df_merged['Доставка'] = pd.to_numeric(df_merged['Доставка'], errors='coerce')

            df_merged['Прибыль'] = df_merged.apply(calculate_result, axis=1)

            # Get the unique values for each column
            unique_values = {}
            for column in df_merged.columns:
                unique_values[column] = df_merged[column].unique()

            # Check for filters
            filter_column = request.POST.get('filter_column')
            filter_value = request.POST.get('filter_value')

            # Filter the data if a filter was selected
            if filter_column and filter_value:
                filtered_rows = []
                for index, row in df_merged.iterrows():
                    if row[filter_column] == filter_value:
                        filtered_rows.append(row)
                context['merged_data'] = filtered_rows
            else:
                # Pass the merged data to the context for rendering in the template
                context['merged_data'] = df_merged.to_dict('records')

            context['unique_values'] = unique_values
            context['form'] = form

            return render(request, 'merged_data.html', context)
    else:
        form = UploadExcelForm()
        context['form'] = form

    return render(request, 'upload_excel.html', context)


def save_changes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        df = pd.DataFrame(data)

        # Save the DataFrame to an Excel file
        output_filename = 'output.xlsx'
        df.to_excel(output_filename, index=False)

        download_url = reverse('download_output')
        return JsonResponse({'status': 'success', 'message': 'Сохранения внесены. Можете скачать файл', 'download_url': download_url})
    else:
        return JsonResponse({'status': 'error', 'message': 'Ошибка.'})

def download_output(request):
    output_filename = 'output.xlsx'
    try:
        if os.path.exists(output_filename):
            response = FileResponse(open(output_filename, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, filename=output_filename)
            return response
        else:
            return JsonResponse({'status': 'error', 'message': 'Файл не найден.'})
    except Exception as e:
        logger.exception("Error in download_output")
        return JsonResponse({'status': 'error', 'message': 'Ошибка сервера. Обратитесь к администратору.'})