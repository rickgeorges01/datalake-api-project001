import csv
from django.core.management.base import BaseCommand
from core.models import Transaction
from datetime import datetime

class Command(BaseCommand):
    help = 'Import transactions from CSV'

    def handle(self, *args, **kwargs):
        path = 'global_superstore_enriched.csv'
        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                reader.fieldnames = [name.strip().replace('\ufeff', '') for name in reader.fieldnames]
                for raw_row in reader:
                    row = {k.strip().replace('\ufeff', ''): v for k, v in raw_row.items()}
                    try:
                        Transaction.objects.update_or_create(
                            row_id=int(row['Row.ID']),
                            defaults={
                                'order_id': row['Order.ID'],
                                'order_date': datetime.strptime(row['Order.Date'], '%Y-%m-%d'),
                                'customer_name': row['Customer.Name'],
                                'country': row['Country'],
                                'product_category': row['Sub.Category'],
                                'payment_method': row['Payment_Method'],
                                'status': row['Status'],
                                'amount': float(row['Sales']),
                                'customer_rating': float(row['Customer_Rating']),
                            }
                        )
                    except Exception as e:
                        self.stderr.write(f"[!] Erreur sur ligne {row.get('Row.ID', 'UNKNOWN')} → {e}")
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"[x] Fichier introuvable à : {path}"))
            return

        self.stdout.write(self.style.SUCCESS("✅ Import terminé avec succès"))
