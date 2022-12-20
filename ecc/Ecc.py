from tinyec.ec import SubGroup, Curve
from tinyec import registry


field = SubGroup(p=15424654874903, g=(6478678675, 5636379357093),n =1,h =1)
curve = Curve(a=16546484, b=4548674875, field=field, name='p1707')
print('curve:', curve)
k = 546768
p = k * curve.g
print(f"{k} * G' = ({p.x}, {p.y})")
print("~~~~~~~~~~~~~~~~~~")

field = SubGroup(p=17, g=(15, 13), n=18, h=1)
curve = Curve(a=0, b=7, field=field, name='p1707')
print('curve:', curve)



field = SubGroup(p=17, g=(5, 9), n=18, h=1)
curve = Curve(a=0, b=7, field=field, name='p1707')
print('curve:', curve)

for k in range(0, 25):
    p = k * curve.g
    print(f"{k} * G' = ({p.x}, {p.y})")


curve = registry.get_curve('secp192r1')
print('curve:', curve)

for k in range(0, 10):
    p = k * curve.g
    print(f"{k} * G = ({p.x}, {p.y})")

print("Cofactor =", curve.field.h)

print('Cyclic group order =', curve.field.n)

nG = curve.field.n * curve.g
print(f"n * G = ({nG.x}, {nG.y})")