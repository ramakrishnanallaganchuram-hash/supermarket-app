from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

store = ['onion','tomato','brinjal','ladiesfinger','potato','cabbage','capsicum',
         'corriander','beetroot','carrot','califlower','avocado','broccoli','ginger',
         'cucumber','bottleguard','spinach','dal','beans','paneer','mushroom']
quantity = [23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23,23]
price    = [20,15,60,40,50,90,65,10,75,60,90,120,80,20,30,35,25,55,40,75,50]

s_customer = []
s_items    = []
s_qnty     = []
s_price    = []

def get_inventory():
    return [{"item": store[i], "quantity": quantity[i], "price": price[i]} for i in range(len(store))]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/admin/inventory', methods=['GET'])
def admin_inventory():
    return jsonify(get_inventory())

@app.route('/api/admin/update', methods=['POST'])
def admin_update():
    data = request.json
    item = data.get('item','').strip().lower()
    qty  = float(data.get('quantity', 0))
    pr   = int(data.get('price', 0))
    mode = data.get('mode', 'add')
    if item in store:
        idx = store.index(item)
        if mode == 'set':
            quantity[idx] = qty
            price[idx] = pr
        else:
            quantity[idx] += qty
            price[idx] += pr
        return jsonify({"status": "updated", "item": item})
    else:
        store.append(item)
        quantity.append(qty)
        price.append(pr)
        return jsonify({"status": "added", "item": item})

@app.route('/api/admin/remove', methods=['POST'])
def admin_remove():
    data = request.json
    item = data.get('item','').strip().lower()
    if item in store:
        idx = store.index(item)
        store.pop(idx)
        quantity.pop(idx)
        price.pop(idx)
        return jsonify({"status": "removed", "item": item})
    return jsonify({"status": "not_found"}), 404

@app.route('/api/admin/sales', methods=['GET'])
def admin_sales():
    sales = []
    for i in range(len(s_items)):
        sales.append({
            "customer": s_customer[i] if i < len(s_customer) else "-",
            "item": s_items[i],
            "quantity": s_qnty[i],
            "price": s_price[i]
        })
    return jsonify({"sales": sales, "total": sum(s_price)})

@app.route('/api/customer/products', methods=['GET'])
def customer_products():
    return jsonify(get_inventory())

@app.route('/api/customer/add_to_cart', methods=['POST'])
def add_to_cart():
    data     = request.json
    customer = data.get('customer','Guest')
    item     = data.get('item','').strip().lower()
    qty      = int(data.get('quantity', 1))
    if item not in store:
        return jsonify({"status": "error", "msg": str(item) + " is not available"}), 400
    idx = store.index(item)
    if qty > quantity[idx]:
        return jsonify({"status": "error", "msg": "Only " + str(quantity[idx]) + " kg available"}), 400
    quantity[idx] -= qty
    total_price = price[idx] * qty
    s_customer.append(customer)
    s_items.append(item)
    s_qnty.append(qty)
    s_price.append(total_price)
    return jsonify({"status": "added", "item": item, "qty": qty, "price": total_price})

@app.route('/api/customer/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data     = request.json
    customer = data.get('customer','Guest')
    item     = data.get('item','').strip().lower()
    qty      = int(data.get('quantity', 1))
    if item in store:
        idx = store.index(item)
        quantity[idx] += qty
    for i in range(len(s_items)-1, -1, -1):
        if s_items[i] == item and s_customer[i] == customer:
            s_items.pop(i)
            s_qnty.pop(i)
            s_price.pop(i)
            s_customer.pop(i)
            break
    return jsonify({"status": "removed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
