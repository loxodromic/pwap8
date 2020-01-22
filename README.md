# pwap8

Add Progressive Web App features to PICO-8 html exports


Copyright (c) 2020 Loxodromic
See LICENSE file.


I love PICO-8. This project is in no way endorsed by Lexaloffle Games. I 
strongly urge you to do yourself a favour and buy a copy from: 
https://www.pico-8.com


PICO-8 can export to HTML + JavaScript. That is really cool and lets you
play your game in a browser.


This hack adds a few bits and bobs to that export to enable 
"progressive web app" features. Most useful of which is that your game will
work offline after it's been played the first time. Handy for playing when 
you're offline. When viewed for the first time, the browser may even ask you 
if you want to "install" this app.


These days, modern browsers give you the option to "install" your app. 
Imagine that: your own game, on your own homescreen, available anywhere.


It does this:
 + By adding a manifest
 + Creating a few icons and whatnot that Google's Lighthouse audit likes
 + Creating a service worker to initially cache, then serve files when offline
 + Adding some noddy content to display when JavaScript is disabled (another Lighthouse warning)


 There are a Visual Studio projects and a solution. That was just for my 
 convenience, the code should be standard Python 3.

 
 Although I've released this project under a MIT licence, if you pass your 
 pride and joy through this utility, then as far as I'm concerned, it's still
 yours. This tool is just a conduit, if what comes in is yours, then what 
 comes out the other end still is.


Have fun, let me know if you have any issues.
 

## Requirements

 + Python 3
 + BeautifulSoup4 (e.g. `pip install bs4')
 + Pillow (e.g. `pip install pillow')
 

## Usage

Export your game from PICO-8. For example, from the PICO-8 command-line:


```
cd test
load test.p8
export -f test.html
```


Then run the pwap8.py code to add progressive web app features:


```
cd test
python ..\..\pwap8pwap8.py --name "test app" --short test  --html test_html/index.html --js test_html/test.js
```

You may want to delete the build directory between runs.


Various options are available: `python pwap8.py --help`


You can specify an image to use as the basis for the icons. You can try the 
cartridge save file p8.png if you like. It looks OK, although the save 
information will likely be lost / damaged by the scaling. The source file 
isn't changed. If you don't provide an image, one is created for you 
(don't get excited, it isn't much to look at). Small images are scaled using 
nearest pixel interpolation, larger images using bicubic (TODO: make this user selectable). 


For testing purposes there is a very simple Python http server in the simple_server dir.
Run `python simple_server.py` from the build directory.


Either use that for local testing, or copy to your favourite host, in my case I uploaded the 
test above to https://loxodromic.github.io/pwatest/


You can now "install the app" when you visit the site.


Gaming on the go, excellent.


## TODO

+ This has only been tested on PICO-8 v0.1.12c. All sorts of assumptions are 
made about the exported HTML. Those are likely to break with future 
versions of PICO-8.
+ There are too many command-line options required for a quick build. It should 
be possible to intelligently pick out some of those values from just a given 
export directory.
+ It might be cool to allow the manifest, service worker and 
icons to be stored inline. Along the same lines as the existing PICO-8 exports.
+ Add options for icon image scaling method (nearest, bicubic, etc) and favicon style (png, ico).
+ More documentation is always nice.
+ Extract icon graphic from .p8 screengrab (F7).
+ There is almost no error checking / exception handling, expect crash reports.


## Version history

1.0.0: [22 Jan 2020] begin at the beginning
1.0.1: [22 Jan 2020] fix to allow the files to be served from a sub-dir
