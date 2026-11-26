from django.core.management.base import BaseCommand
from myapp.models import Product

PRODUCTS = [
 ('Hybrid Maize Seeds 2kg','Seeds','Certified hybrid maize seed for strong germination and good yields.',650,45,'https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=700&q=80',True),
 ('Tomato Seeds 10g','Seeds','Quality tomato seeds suitable for kitchen gardens and commercial growing.',280,60,'https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=700&q=80',True),
 ('NPK Fertilizer 25kg','Fertilizers','Balanced fertilizer for healthy root development and crop growth.',3200,25,'https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&w=700&q=80',True),
 ('CAN Fertilizer 25kg','Fertilizers','Top-dressing fertilizer to support vigorous crop growth.',2450,30,'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=700&q=80',False),
 ('Crop Protection Spray 1L','Crop Protection','General crop protection product. Follow the label and local professional advice.',890,18,'https://images.unsplash.com/photo-1586771107445-d3ca888129ff?auto=format&fit=crop&w=700&q=80',True),
 ('Poultry Vitamin Supplement 100ml','Animal Health','Vitamin supplement for poultry. Use according to product label and veterinary guidance.',420,40,'https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?auto=format&fit=crop&w=700&q=80',False),
 ('Dairy Meal 70kg','Animal Feeds','Dairy animal feed for balanced nutrition. Check feed instructions before use.',2850,20,'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=700&q=80',True),
 ('Grade 1 Dry Beans 2kg','Grains','Clean, sorted dry beans for household use.',460,50,'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=700&q=80',False),
 ('White Maize Grain 10kg','Grains','Clean maize grain, packed for convenient storage.',780,35,'https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=700&q=80',False),
 ('Garden Hand Hoe','Farm Tools','Durable hand hoe for everyday garden and small-farm work.',550,22,'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=700&q=80',True),
 ('Pruning Shears','Farm Tools','Handy pruning shears for trimming and routine garden maintenance.',690,15,'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=700&q=80',False),
]

class Command(BaseCommand):
    help = 'Create sample products only when they do not already exist.'
    def handle(self, *args, **options):
        for name, category, description, price, stock, image, featured in PRODUCTS:
            Product.objects.get_or_create(name=name, defaults={
                'category': category, 'description': description, 'price': price,
                'stock': stock, 'image_url': image, 'featured': featured, 'active': True,
            })
        self.stdout.write(self.style.SUCCESS(f'Checked {len(PRODUCTS)} sample products; existing products were left unchanged.'))
