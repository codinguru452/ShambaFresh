# ShambaFresh Agrovet — Django + JavaScript + Bootstrap

A local-first agrovet ecommerce demo built on the Django project in the supplied `MpesaIntegration2026-master` archive. It includes a product catalogue, category filters/search, session cart, checkout, order records, Django admin, and Safaricom Daraja STK Push with a callback endpoint.

## 1. Requirements
- Python 3.10+
- Internet connection for Bootstrap, icons, Google Fonts and product photos (the app itself runs locally)

## 2. Install and run (Windows PowerShell)
Open PowerShell in the project folder:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
py manage.py migrate
py manage.py seed_products
py manage.py createsuperuser
py manage.py runserver
```

Open **http://127.0.0.1:8000/**. Admin is at **http://127.0.0.1:8000/admin/**. Sign in with the superuser you created to add/edit products and view orders.

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```

## 3. Configure M-Pesa STK Push (Daraja sandbox)
The integration uses the Daraja OAuth token endpoint and `mpesa/stkpush/v1/processrequest`. The sample credentials from the uploaded source have intentionally **not** been copied: credentials must be private and should be rotated if they were real.

1. Create/use a Safaricom Daraja developer app and obtain its **sandbox** consumer key and consumer secret.
2. Put `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, and `MPESA_PASSKEY` in `.env`.
3. Set `MPESA_CALLBACK_URL` to a publicly reachable HTTPS URL ending in `/mpesa/callback/`. Safaricom cannot call `localhost` directly. For local callback testing, expose the local server with a trusted HTTPS tunnel (for example, ngrok) and use that tunnel URL.
4. Keep `MPESA_BASE_URL=https://sandbox.safaricom.co.ke` while testing. Use only sandbox test numbers and sandbox-approved credentials.
5. Restart Django after editing `.env`.

When a customer submits checkout, the server sends the STK Push request. The customer enters their M-Pesa PIN on their phone. Safaricom then posts the result to `/mpesa/callback/`, which updates the order to PAID or FAILED and records the receipt number. The order status page refreshes while the order is pending.

**Important:** Without valid Daraja credentials and a reachable callback URL, the store and cart still work, but a real STK prompt will not be sent. This project is a development starter, not a production payment system. Before production, add HTTPS deployment, stronger callback verification/reconciliation, rate limiting, inventory reservation/expiry, email/SMS notifications, privacy controls, logging/monitoring and production credentials. Do not collect or store an M-Pesa PIN in this website.

## 4. Useful URLs
- `/` — shop
- `/cart/` — cart
- `/checkout/` — checkout and STK Push
- `/orders/<id>/` — order status
- `/mpesa/callback/` — Safaricom callback (POST)
- `/admin/` — product and order management

## 5. Notes
- Prices are sample KSh values; edit them in Django admin.
- Products and orders are stored in SQLite by default.
- Cart contents are stored in the Django session.
- Product images are external Unsplash URLs; replace them with your own licensed product photos in admin.
