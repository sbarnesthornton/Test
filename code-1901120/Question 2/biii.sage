# Finds all the values of g^a (mod 31) for which pollard-rho fails where g is 3
# g^a must be between 0 and 30
# if pollard rho fails, then the gcd(|b[i]-b[j]|, 30) > 1
failed = []
succeeded = []
for ga in range(0,31):
    j=0
    g=3
    o=31
    G = [3]
    b = [1]
    c = [0]
    newVals = (0,0,0)
    while (newVals[0] not in G):
        if newVals != (0,0,0):
            G.append(newVals[0])
            b.append(newVals[1])
            c.append(newVals[2])
        if (G[j]%3) == 0:
            newVals = ((G[j] * g)%o, (b[j] + 1)%o, (c[j])%o)
        elif G[j]%3 == 1:
            newVals = ((G[j] * ga)%o, (b[j])%o, (c[j] + 1)%o)
        elif G[j]%3 == 2:
            newVals = ((G[j] * G[j])%o, (2*b[j])%o, (2*c[j])%o)
        j += 1
    i = G.index(newVals[0])
    if gcd(abs(b[i]-newVals[1]), 30) > 1:
        failed.append(ga)
    else:
        succeeded.append(ga)
print("Failed: ", failed)
print("Succeeded", succeeded)