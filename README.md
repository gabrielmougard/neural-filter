# neural-filter

The work is still in progress but it's possible to run the script and obtain decent results...

However, you must fill a couple of conditions : 
  - Especially some python modules (listed below):
      * Tensorflow ( 1.0 or higher, for my part I use the 1.0 )
      * Scipy ( that's a must have ! You shall update it to the newest version or just install it with the command : ' sudo pip install          scipy' ==> If you're on a Linux system. Though, you may have a Windows system ; So if pip doesn't work properly you can use easy_install provided with latest python version (For now, I think it's 3.5 ) . if you still encounter some problems, google it 'how to install Scipy on my laptop) ==> it's an easy one, everything is well documented, you should get rid of it ;)
      * os ( already installed )
      * argparse ( already installed )  
      * numpy ( you must get the newest version )
      * math (already installed)
      * PIL ( Python Imaging Library ) 
      * functools
      
  - Moreover, you've to download ' imagenet-vgg-verydeep-19.mat ' which is the network you're going to use. That's a big one ( ~550Mo) but it's quite powerful... You can find it at http://www.vlfeat.org/matconvnet/pretrained/
  You can put it in your working directory... It'll work for the future. Or you can use the argument `--network <path/of/your/file>`
  
  
  ## HOW TO 
  
  * first you have to open a terminal and change your current directory to your working directory 
  * Then you can enter the following command ( it's and example ):
  
    `py neural_filter.py --content C:\Users\gabri\Pictures\max.png --styles C:\Users\gabri\Pictures\gogh.png --output image_sortie.png --iterations 10`
  
     (if your PATH isn't 'py', replace it with your PATH calling python) 
     
the files `max.png` and `gogh.png` in the command, are respectively the base image and the style image ( see below...)
![base_image](Pictures/max.png)
![style_image](Pictures/gogh.png)

the resulting picture is quite disgusting ( Though, I precised only 10 iterations in argument so it's normal)
![output_image](Pictures/image_sortie.png)


* And now with 100 iterations ( I have to say that the process is extremely loooong ! (if you are using your CPU instead of your GPU)
  - For my part, I had a new laptop ( running on windows 10 ) and the compatibility between TensorFlow en widows suck ! So I am still   trying to install TensorFlow-GPU but you may encounter a bunch of problems !! ( Vive Linux ! )
  
* command :

  `py neural_filter.py --content C:\Users\gabri\neural-filter\max.png --styles C:\Users\gabri\neural-filter\gogh.png --output output_image.png --iterations 100`
  
* Result : 
![output_image](Pictures/100iterations.png)

(It is important to notice that color-preservation has been avoided in this picture...)
We can easily figure it out with the argument : `--preserve-colors True`

## Quick Conclusion :

Running the program on windows 10 (i.e with no TensorFlow-GPU ), I had to wait almost 2 hours to have the 100 iterations picture.
The speed could be really increased ( 3-4 minutes for 1000 iterations) with a good GPU ( very good...) and a Linux system with TensorFlow-GPU installed and configured !
