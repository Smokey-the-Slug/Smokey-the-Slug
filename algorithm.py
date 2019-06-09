# Import the cv2 library
import cv2, numpy as np
# Read the image you want connected components of
def rgb_threshold(step):
    rgb_anomaly = 0
    image = cv2.imread('RGB_high%d.jpg' % step)
    # Threshold it so it becomes binary
    gray = (image[:,:,0]/3+image[:,:,1]/3+image[:,:,2]/3)
    gray = gray.astype(np.uint8)
    gray = cv2.blur(gray,(10,10))
    
    ret, thresh = cv2.threshold(gray,235,1,cv2.THRESH_BINARY)
    # You need to choose 4 or 8 for connectivity type
    connectivity = 8  
    # Perform the operation
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    # Extract states
    stats = output[2]
    # Discriminate by size
    for i,j in enumerate(stats[:,4]):
        if i > 0 and 0 < j < 10000:
            rgb_anomaly = 1
    return rgb_anomaly, thresh

def lep_threshold(step):
    
    image = np.zeros([60,80], np.float64)
    file = open('lepton%d.pgm' % step, 'r')
    content = file.readlines()
    file.close()
    for i in range(60):
        oneline = content[i+3].split(' ')
        for j in range(80):
            image[i,j] = oneline[j]
    
    # Threshold it so it becomes binary
    ret, thresh = cv2.threshold(image,8400,1,cv2.THRESH_BINARY)
    # You need to choose 4 or 8 for connectivity type
    connectivity = 8  
    # Perform the operation
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    # Extract states
    stats = output[2]
    # Discriminate by size
    for i,j in enumerate(stats[:,4]):
        if i > 0 and 0 < j < 25:
            lep_anomaly = 1
    return lep_anomaly, thresh

def ColorProcess(step):
    
    I = cv2.imread('RGB_low%d.jpg' % step)
    #cv2.imshow('original', I)
    [ir ,ic, dim] = I.shape
    #print(ir)
    #print(ic)
    ##separating RGB color channels
    rchannel = I[:, :, 2]
    #print(rchannel.shape)
    #cv2.imshow('red channel', rchannel)
    gchannel = I[:,:,1]
    #cv2.imshow('green channel', gchannel)
    bchannel = I[:,:,0]
    #cv2.imshow('blue channel', bchannel)
    
    
    ##RGB to YCbCr color channels
    Y = 16+(0.2567890625  * rchannel) + (0.50412890625 * gchannel) + ( 0.09790625 * bchannel)
    Cb= 128+(-0.14822265625 * rchannel) - (0.2909921875 * gchannel) + (0.43921484375* bchannel)
    Cr = 128+(0.43921484375  * rchannel) - (0.3677890625 * gchannel) - ( 0.07142578125 * bchannel)
    #print(Y)
    #print(Cb)
    #print(Cr)
    #print(Crstd)
    
    ##rule 3 & 4
    [R34r, R34c] = np.where(((Y > Cr) & (Cb < Cr) & (Cr>152)) | (Cr > 152))
    R34r = np.transpose([R34r])
    ruleVpixel = R34r.shape[0]
    #print(R34r.shape)
    Ir34 = np.zeros((I.shape), dtype=np.uint8)
    for i6 in range (ruleVpixel - 1):
        Ir34[R34r[i6],R34c[i6],2] =rchannel[R34r[i6],R34c[i6]]
        Ir34[R34r[i6],R34c[i6],1] =gchannel[R34r[i6],R34c[i6]]
        Ir34[R34r[i6],R34c[i6],0] =bchannel[R34r[i6],R34c[i6]]
    
    #F = cv2.add(Ir12, Ir34)
    #F = cv2.bitwise_and(Ir12, Ir34)
    #F = Ir34
    rch = Ir34[:,:,2]
    gch = Ir34[:,:,1]
    bch = Ir34[:,:,0]
    #cv2.imwrite('firedet.jpg', F)
    #cv2.imshow('F',F)
    #cv2.imshow('rch',rch)
    #cv2.imshow('gch',gch)
    #cv2.imshow('bch',bch)
    
    #[R5r, R5c] = np.where((F[:,:,2] > F[:,:,0]) & (F[:,:,1] > F[:,:,0]) & (F[:,:,0] < 150))
    
    [R5r, R5c] = np.where((rch > bch) & (gch > bch) & (bch < 150))
    R5r = np.transpose([R5r])
    [r, c] = rchannel.shape
    E = np.zeros((ir,ic), dtype=np.uint8)
    for p in range (0, ir):
        for q in range (0, ic):
            if ((rch[p,q] > bch[p,q]) and (gch[p,q] > bch[p,q]) and (bch[p,q]<150)):
                 E[p,q] = 255 #use 255 instead of 1 to make a binary image
            else:
                 E[p,q] = 0           
    #print(r)
    #print(R5r.shape)
    #print(R5c)
    [Fr, Fc] = R5r.shape
    #print(Fr)
    #print(Fc)
    
    x = (r * c * 3/100)
    #print(x)
    if Fr > x:
        flag = 1
    else:
        flag = 0
    #Flag is the anomaly, F is color, E is uint8 binary
    return (flag, E) 