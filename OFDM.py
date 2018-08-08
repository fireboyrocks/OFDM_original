
import numpy as np
import matplotlib.pyplot as plt

"""
System Parameters decription
"""
K = 64 # number of OFDM subcarriers
CP = K//4 # length of cyclic prefix


P = 8 # number of pilot carriers per OFDM block
pilotValue = 3+3j # the known value each pilot transmits


allCarriers = np.arange(K) # indices of all subcarriers

pilotCarriers = allCarriers[::K//P] # Pilots is every (K/P)th carrier


# for convinience of channel estimation, let's make the last carriers also be a pilot
pilotCarriers = np.hstack([pilotCarriers,np.array([allCarriers[-1]])])
P = P + 1

# data carriers are all remaining carriers
dataCarriers = np.delete(allCarriers, pilotCarriers)


print("allCarriers: %s" % allCarriers)
print("pilotCarriers: %s" % pilotCarriers)
print("dataCarriers: %s" %dataCarriers)
plt.figure(1)
plt.plot(pilotCarriers, np.zeros_like(pilotCarriers), 'bo', label = 'pilot')
plt.plot(dataCarriers, np.zeros_like(dataCarriers), 'ro', label = 'data')



"""
Modulation 
"""
mu = 4 # bits per symbol (here 16 QAM)
payloadBits_per_OFDM = len(dataCarriers)*mu # number of payload bits per OFDM symbol

mapping_table = {
        (0,0,0,0) : -3-3j,
        (0,0,0,1) : -3-1j,
        (0,0,1,0) : -3+3j,
        (0,0,1,1) : -3+1j,
        (0,1,0,0) : -1-3j,
        (0,1,0,1) : -1-1j,
        (0,1,1,0) : -1+3j,
        (0,1,1,1) : -1+1j,
        (1,0,0,0) : 3-3j,
        (1,0,0,1) : 3-1j,
        (1,0,1,0) : 3+3j,
        (1,0,1,1) : 3+1j,
        (1,1,0,0) : 1-3j,
        (1,1,0,1) : 1-1j,
        (1,1,1,0) : 1+3j,
        (1,1,1,1) : 1+1j        
        }

plt.figure(2)
for b3 in [0,1]:
    for b2 in [0,1]:
        for b1 in [0,1]:
            for b0 in [0,1]:
                B = (b3, b2, b1, b0)
                Q = mapping_table[B]
                plt.plot(Q.real,Q.imag,'bo')
                plt.text(Q.real,Q.imag+0.2, "".join(str(x) for x in B), ha='center')
                
                

demapping_table = {v : k for k, v in mapping_table.items()}


"""
Wireless channel
"""
channelResponse = np.array([1, 0, 0.3+0.3j]) # the impulse response of the wireless channel
H_exact = np.fft.fft(channelResponse,K)
plt.figure(3)
plt.plot(allCarriers, abs(H_exact))
SNRdb = 25 # signal to noise-ratio in dB at the Rx



"""
Making the input signal
"""
bits = np.random.binomial(n=1, p=0.5, size=payloadBits_per_OFDM)
print ("Bits count: ", len(bits))
print ("First 20 bits: ", bits[:20])
print ("Mean of bits (should be around 0.5): ", np.mean(bits))



"""
S/P converter
"""
def SP(bits):
    return bits.reshape((len(dataCarriers), mu))
bits_SP = SP(bits)
print ("First 5 bit groups")
print (bits_SP[:5,:])



def Mapping(bits):
    return np.array([mapping_table[tuple(b)] for b in bits])
QAM = Mapping(bits_SP)
print ("First 5 QAM symbols and bits:")
print (bits_SP[:5,:])
print (QAM[:5])



"""
Allocation of data to carriers
For instance giving data to pilot and data subcarriers
"""
def OFDM_symbol(QAM_payload):
    symbol = np.zeros(K, dtype=complex) # overall K subcarriers
    symbol[pilotCarriers] = pilotValue # allocate the pilot subcarriers
    symbol[dataCarriers] = QAM_payload # allocate the pilot subcarriers
    return symbol
OFDM_data = OFDM_symbol(QAM)
print ("Number of OFDM carriers in frequency domain:", len(OFDM_data))


"""
Conversion to time-domain
"""
def IDFT(OFDM_data):
    return np.fft.ifft(OFDM_data)
OFDM_time = IDFT(OFDM_data)
print ("Number of OFDM samples in time-domain before CP: ", len(OFDM_time))



"""
Addition of CP
"""
def addCP(OFDM_time):
    cp = OFDM_time[-CP:] # take the last CP samples
    return np.hstack([cp,OFDM_time]) # add the CP to the beginning
OFDM_with_CP = addCP(OFDM_time)
print ("Number of OFDM samples in time domain with CP: ", len(OFDM_with_CP))



"""
Addition of noise and multiplication with channel
"""
def channel(signal):
    convolved = np.convolve(signal, channelResponse)
    signal_power = np.mean(abs(convolved**2))
    sigma2 = signal_power * 10**(-SNRdb/10) # calculate noise power based on signal power and SNR
    print ("RX signal power: %.4f. Noise power: %.4f" % (signal_power, sigma2))

    # Generate complex noise with given variance
    noise = np.sqrt(sigma2/2) * (np.random.randn(*convolved.shape) + 1j*np.random.randn(*convolved.shape))     
    return convolved + noise

OFDM_TX = OFDM_with_CP
OFDM_RX = channel(OFDM_TX)

plt.figure(4)
plt.figure(figsize = (8,2))
plt.plot(abs(OFDM_TX), label = 'TX signal')
plt.plot(abs(OFDM_RX), label = 'RX signal')
plt.legend(fontsize = 10)
plt.xlabel('time')
plt.ylabel('$|x(t)|$')
plt.grid(True)


"""
At Rx, remove CP
"""
def removeCP(signal):
    return signal[CP:(CP+K)]
OFDM_RX_noCP = removeCP(OFDM_RX)


"""
Transform to frequency domain
"""
def DFT(OFDM_RX):
    return np.fft.fft(OFDM_RX)
OFDM_demod = DFT(OFDM_RX_noCP)



    




    




    