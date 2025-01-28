import pandas as pd
from django.core.management.base import BaseCommand
from trades.models import Item

class Command(BaseCommand):
    help = 'Import items from Excel file into the database'

    def handle(self, *args, **kwargs):
        file_path = 'Тест.xlsx' # Замените на путь к вашему файлу
        data = pd.read_excel(file_path)

        for _, row in data.iterrows():
            Item.objects.create(
                name=row['Наименование комплектующей'],
                price=row['Цена']
            )

        self.stdout.write(self.style.SUCCESS('Items imported successfully'))
