import re
import pytesseract
from PIL import Image
import difflib

# Get information from the receipt
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/Cellar/tesseract/5.3.4_1/bin/tesseract'
info = pytesseract.image_to_string(Image.open('test.png'))

lines = info.strip().split('\n')
dishes = []
prices = []

# Define regex pattern to extract items and prices
pattern = re.compile(r'\b(\D+?)\s+(\d+[.,]\d{2})')

# Iterate over each line and extract items and prices
for line in lines:
    match = pattern.search(line)
    if match:
        dish, price = match.groups()
        dishes.append(dish.strip())
        prices.append(float(price.replace(',', '.')))

dishes = [x.lower() for x in dishes]

# Get subtotal and tax and delete the rest (total is useless since you tax and tip on subtotal)
tax = prices[-2]
subtotal = prices[-3]

# Last 3 dishes/prices are subtotal, tax, total, so remove them
del dishes[-3:]
del prices[-3:]

# Get the people that are at the meal
print("Who's there? separate by commas")
eaters = str(input())
people = eaters.split(',')
people = [x.lower() for x in people]

numLists = len(people)
orders = [[] for _ in range(numLists)]

# Get indices of the items each person got
for i in range(len(people)):
    orders[i].append(people[i])
    print("What did " + people[i] + " eat?")
    order = str(input())
    items = order.split(',')
    items = [x.lower() for x in items]
    for item in items:
        guess = difflib.get_close_matches(item, dishes, n=1, cutoff=0.1)
        if guess:  # Ensure there is a match
            index = dishes.index(guess[0])
            orders[i].append(index)

for order in orders:
    indices = order[1:]
    total_price = sum(prices[index] for index in indices)
    order.append(total_price)

for order in orders:
    indices = order[1:-1]
    items_ordered = [dishes[index] for index in indices]
    items_str = ', '.join(items_ordered)
    order.append(items_str)

# Ask who fronted the bill, so they don't have to pay anything later
payer = input("Who paid? ").lower()

valid_payer = False
while not valid_payer:
    for order in orders:
        if payer == order[0].lower():
            valid_payer = True
            break
    if not valid_payer:
        payer = input("Invalid payer. Please enter who paid: ").strip().lower()

# Calculate and print the amount each person owes the payer
for i in range(len(orders)):
    if orders[i][0].lower() != payer:
        amount_owed = orders[i][-2] + orders[i][-2] * 0.15 + (orders[i][-2] / subtotal) * tax
        print(f"The amount {orders[i][0]} owes {payer.capitalize()} for the {orders[i][-1]} is: {round(amount_owed, 2)}")
