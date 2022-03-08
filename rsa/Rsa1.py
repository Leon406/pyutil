import gmpy2

# 已知p,q,e，获取d
p = gmpy2.mpz(336771668019607304680919844592337860739)
q = gmpy2.mpz(296173636181072725338746212384476813557)
e = gmpy2.mpz(65537)
phi_n = (p - 1) * (q - 1)
d = gmpy2.invert(e, phi_n)
print("d is:")
print(d)
