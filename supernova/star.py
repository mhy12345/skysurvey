import cv2
import numpy as np
from img_utils import image_quality, masked_similarity, star_ratio

class Star:
    def __init__(self, name, path = None):
        self.name = name
        self.path = path
        img = cv2.imread(self.img_path , cv2.IMREAD_GRAYSCALE)
        if img is None:
            print("File "+name+".png not found.")
            exit(0)
        img = img.astype(np.float32)/256
        img_base, img_cur, img_sdiff = img[:,:240], img[:, 240:480], img[:, 480:] 

        self._img_base = img_base
        self._img_cur  = img_cur
        self._img_sdiff= img_sdiff

        # Blur
        img_base = cv2.bilateralFilter(img_base, 9, 75, 75)
        img_cur  = cv2.bilateralFilter(img_cur , 9, 75, 75)
        img_sdiff  = cv2.bilateralFilter(img_sdiff , 9, 75, 75)
        img_diff = - img_base + img_cur + .5

        self.images = img
        self.img_base = img_base
        self.img_cur = img_cur 
        self.img_sdiff = img_sdiff
        self.img_diff = img_diff
        self._properties = None

    @property
    def quality(self):
        return min(image_quality(self._img_cur), image_quality(self._img_base))

    @property
    def similarity(self):
        return masked_similarity(self.img_cur, self.img_base)

    @property
    def star_ratio(self):
        return star_ratio(self.img_base, self.img_cur)

    @property
    def raw_images(self):
        return np.concatenate(
            [
                self.img_base, 
                self.img_cur, 
                self.img_diff, 
                self.img_sdiff
                ], 1)
    
    @property
    def brightness(self):
        '''
        import matplotlib.pyplot as plt
        plt.imshow(self.img_base)
        plt.show()
        ''' 
        v1 = self.img_base[110:130,110:130].min()
        v2 = self.img_cur[110:130,110:130].min()
        return v1,v2

    @property
    def brightness_shift(self):
        r2 = -self.img_diff[110:130,110:130].min()+self.img_diff.mean()
        return r2

    @property
    def properties(self):
        if self._properties is not None:
            return self._properties
        res = {}
        res['name'] = self.name
        res['ratio'] = self.star_ratio
        res['quality'] = self.quality
        res['similarity'] = self.similarity
        res['brightness'] = self.brightness
        res['brightness_shift'] = self.brightness_shift
        self._properties = res
        return res

    def test(self):
        res = self.properties
        if res['quality'] < 0.9:
            return "NOISE", "Picture quality is bad. (%f < 0.9)" % res['quality']
        if min(res['ratio']) < 0.010:
            return "NOISE", "Stars are too small. (%f < 0.01)" % min(res['ratio'])
        if res['similarity'] < 0.025:
            return "NOISE", "Similarity not enough. (%f < 0.025)" % res['similarity']
        # c20190610_1_NT0064_L_591_00004 0.056693761291077692 NO
        # c20190610_1_NT0060_L_615_00001 0.083477433193531597 YES
        if res['brightness'][1] > 0.3:
            return "NOISE", "Not bright enough today. (%f > 0.3)" % res['brightness'][1]
        # c20190610_1_NT0142_L_357_00000 0.263147 YES
        if res['brightness_shift'] < 0.2:
            return "VARIABLE_STAR", "Variable Star, not supernova. (%f < 0.2)" % res['brightness_shift']
        if res['brightness'][0] < 0.2:
            return "VARIABLE_STAR", "Variable Star, not supernova. (%f < 0.2)" % res['brightness'][0]
        return "SUPERNOVA", "Check pass."

    @property
    def img_path(self):
        if self.path is not None:
            return self.path
        return './images/'+ self.name + '.png'
        


def star_iterator(date = None):
    import os
    import re
    if date is None:
        res = os.listdir('./images')
        res = sorted(res)
        for w in res:
            if re.match(r'2019\d{4}$', w) is None:
                continue
            for s in star_iterator(w):
                yield s
    else:
        path = './images/'+date+'/png/'
        stars = os.listdir(path)
        for sname in stars:
            if re.match(r'\S*\.png', sname) is None:
                continue
            yield sname[:-4], path + sname

if __name__ == '__main__':
    slist = star_iterator()
    for w in slist:
        print(w)
