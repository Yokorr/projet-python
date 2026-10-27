raw_customers = [
    "  alice MARTIN ;ALICE@pymart.com; 06 12 34 56 78",
    "bob  durand;bob.durand@pymart;0612345679",
    "  chloé LEROY ;chloe@pymart.com;+33 6 12 34 56 80",
]

def normalize_name(raw_name):
    return " ".join(raw_name.split()).title()

def is_valid_email(email):
    email = email.strip().lower()
    if email.count("@") != 1:
        return False
    local, domain = email.split("@")
    has_dot = "." in domain and not domain.endswith(".")
    return bool(local) and has_dot

def format_phone(phone):
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("33"):
        digits = "0" + digits[2:]
    pairs = [digits[i:i + 2] for i in range(2, 10, 2)]
    return f"+33 {digits[1]} {' '.join(pairs)}"

print(f"{'NAME':<14}{'PHONE':<19}STATUS")
for line in raw_customers:
    name, email, phone = line.split(";")
    ok = is_valid_email(email)
    print(
        f"{normalize_name(name):<14}"
        f"{format_phone(phone):<19}"
        f"{'OK' if ok else 'INVALID'}"
    )