# Peforms baby-step-giant-step
# Computes a s.t 716^a = 633 (mod 829)
B = [(716**i)%829 for i in range(0,29)]
C = [(633*(716**(-28))**j)%829 for j in range(0,30)]
for j in range(len(C)):
    for i in range(len(B)):
        if B[i] == C[j]:
            print("a: ", i + j*(28))
            break