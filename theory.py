import numpy as np

Vdd = 10 #V
Pout = 5 #W
Zout = 50 #Ohms
f = 100E6 #Hz
L2_Q = 10

RL = 1.154 * np.power(Vdd,2) * (1/(2*Pout))
print("RL: %4.4f" %(RL))
L1_min = (100*RL)/(2*np.pi*f)
print("RF Choke min: %.4e" %(L1_min))
L2 = (L2_Q*RL)/(2*np.pi*f)
print("L2: %.4e" %(L2))
C1 =  1/(5.45*2*np.pi*f*RL)
print("C1: %.4e" %(C1))
C2 = 1/(np.power(2*np.pi*f,2)*L2 - (0.212/C1))
print("C2: %.4e" %(C2))
