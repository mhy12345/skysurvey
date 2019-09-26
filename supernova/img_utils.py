import numpy as np

def image_quality(img):
    _img = (img*256).astype(np.uint8).flatten()
    v = np.argmax(np.bincount(_img))
    s = np.sum(_img == v)
    return 1.0 - s / img.size

def masked_similarity(im1, im2):
    import copy
    im1 = copy.deepcopy(im1)
    im2 = copy.deepcopy(im2)
    im1[100:140, 100:140] = im1.mean()
    im2[100:140, 100:140] = im2.mean()
    def normalize(img):
        c_mean, c_std = np.mean(img), np.std(img)
        c_mean = np.quantile(img, 0.2)
        return (img - c_mean) / c_std
    im1 = normalize(im1)
    im2 = normalize(im2)
    sim1 = np.where(im1 < -2.0, -1, 0.05) * np.where(im2 < -1.5, -1, 0.5)
    sim2 = np.where(im2 < -2.0, -1, 0.05) * np.where(im1 < -1.5, -1, 0.5)
    '''
    import matplotlib.pyplot as plt
    plt.subplot(2,2,1)
    plt.imshow(im2)
    plt.subplot(2,2,2)
    plt.imshow(sim1)
    plt.subplot(2,2,3)
    plt.imshow(im2 < 0)
    plt.show()
    '''
    return (np.mean(sim1) + np.mean(sim2))/2


def star_ratio(img1, img2):
    mean1, std1 = np.mean(img1), np.std(img1)
    mean2, std2 = np.mean(img2), np.std(img2)
    std = (std1+std2)/2
    img1 = (img1-mean1)/std1
    img2 = (img2-mean2)/std2
    v1 = (img1 < -2).astype(np.float32).mean() 
    v2 = (img2 < -2).astype(np.float32).mean()
    return (v1, v2)
