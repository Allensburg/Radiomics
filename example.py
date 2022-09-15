# https://youtu.be/tNfcvgPKgyU
"""
Here, we use openslide to read a whole slide image. 
We will then extract a lower reolution version of the image to normalize it
and then to extract H and E signals separately. 

We will also perform the exact operation on the entire whole slide image by 
extracting tilee, processing them, and saving processed images separately. 

Please note that this code will not cover putting tiles back into a 
whole slide image (image pyramid). You can explore pyvips or similar package
to put together tiles into an image pyramid. 

For an introduction to openslide, please watch video 266: https://youtu.be/QntLBvUZR5c
    
For details about H&E normalization, please watch my video 122: https://youtu.be/yUrwEYgZUsA
    
Useful references:
A method for normalizing histology slides for quantitative analysis. M. Macenko et al., ISBI 2009
http://wwwx.cs.unc.edu/~mn/sites/default/files/macenko2009.pdf

Efficient nucleus detector in histopathology images. J.P. Vink et al., J Microscopy, 2013

Other useful references:
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5226799/
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0169875

"""

#import pyvips
from openslide import open_slide
#from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import tifffile as tiff
import openslide
from openslide.deepzoom import DeepZoomGenerator

#Load a level image, normalize the image and digitally extract H and E images
#As described in video 122: https://www.youtube.com/watch?v=yUrwEYgZUsA
from normalize_HnE import norm_HnE


#######################################################

#The way the HnE normalization code is written, it does not work for blank images.
#Also, it does not do a good job with very little regions.

#A few tiles were already saved and in the following exercise we will load them 
#to understand the mean and std. dev. in their pixel values. 
#We can then handle blank tiles and tiles with low sample region separately.


#Let us define a function to detect blank tiles and tiles with very minimal information
#This function can be used to identify these tiles so we can make a decision on what to do with them. 
#Here, the function calculates mean and std dev of pixel values in a tile. 
def find_mean_std_pixel_value(img_list):
    
    avg_pixel_value = []
    stddev_pixel_value= []
    for file in img_list:
        image = tiff.imread(file)
        avg = image.mean()
        std = image.std()
        avg_pixel_value.append(avg)
        stddev_pixel_value.append(std)
        
    avg_pixel_value = np.array(avg_pixel_value)  
    stddev_pixel_value=np.array(stddev_pixel_value)
        
    print("Average pixel value for all images is:", avg_pixel_value.mean())
    print("Average std dev of pixel value for all images is:", stddev_pixel_value.mean())
    
    return(avg_pixel_value, stddev_pixel_value)

#Let us read some blank tiles, some partial tiles and some good ones to find out
#the mean and std dev of pixel values. 
#These numbers can be used to identify 'problematic' slides that we can bypass from our processing. 
import glob
orig_tile_dir_name = "images/original_tiles/"

blank_img_list=(glob.glob(orig_tile_dir_name+"blank/*.tif"))
partial_img_list=(glob.glob(orig_tile_dir_name+"partial/*.tif"))
good_img_list=(glob.glob(orig_tile_dir_name+"good/*.tif"))

blank_img_stats = find_mean_std_pixel_value(blank_img_list)
partial_img_stats = find_mean_std_pixel_value(partial_img_list)
good_img_stats = find_mean_std_pixel_value(good_img_list)

"""
Average pixel value for all blank images is: 244.45962306699482
Average std dev of pixel value for all blank images is: 0.9214953206879862

Average pixel value for all partial images is: 242.93900954932494
Average std dev of pixel value for all partial images is: 10.427143587023263

Average pixel value for all good images is: 208.8701055190142
Average std dev of pixel value for all good images is: 37.36282416278772
"""






 


import os
os.chdir('./example')
os.mkdir('/images/example1/original_tiles',exist_ok=True)
os.mkdir('/images/example1/normalized_tiles',exist_ok=True)
slide = openslide.OpenSlide('example1.svs')
#Objective used to capture the image
objective = float(slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])
tiles = DeepZoomGenerator(slide, tile_size=150, overlap=0, limit_bounds=False)
#Here, we have divided our svs into tiles of size 256 with no overlap. 

###### processing and saving each tile to local directory
cols, rows = tiles.level_tiles[15]
orig_tile_dir_name = "images/example1/original_tiles/"
norm_tile_dir_name = "images/example1/normalized_tiles/"

for row in range(rows):
    for col in range(cols):
        try:

          tile_name = str(col) + "_" + str(row)
          #tile_name = os.path.join(tile_dir, '%d_%d' % (col, row))
          #print("Now processing tile with title: ", tile_name)
          temp_tile = tiles.get_tile(15, (col, row))
          temp_tile_RGB = temp_tile.convert('RGB')
          temp_tile_np = np.array(temp_tile_RGB)
          #Save original tile
          tiff.imsave(orig_tile_dir_name+tile_name + "_example1_original.tif", temp_tile_np)
        
          if temp_tile_np.mean() < 230 and temp_tile_np.std() > 15:
              print("Processing tile number:", tile_name)
              norm_img, H_img, E_img = norm_HnE(temp_tile_np, Io=240, alpha=1, beta=0.15)
          #Save the norm tile, H and E tiles      
            
              tiff.imsave(norm_tile_dir_name+tile_name + "_example1_norm.tif", norm_img)
              #tiff.imsave(H_tile_dir_name+tile_name + "_H.tif", H_img)
              #tiff.imsave(E_tile_dir_name+tile_name + "_E.tif", E_img)
            
          else:
            print("NOT PROCESSING TILE:", tile_name)
        except:
            pass
        continue
      
        
        
####################################################


###################################################

#You can also try using pyvips to create an image pyramid from stored tiles. 