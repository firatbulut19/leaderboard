import pycountry
import random

rand = list(pycountry.countries)
print(random.choice(rand).alpha_2.lower())