#pwap8: A tool to add Progressive Web App elements to PICO-8 HTML exports
#Copyright (c) 2020 Loxodromic
#MIT License (see LICENSE)

#....

from bs4 import BeautifulSoup
from bs4 import Doctype
from PIL import Image

import os
import json
import shutil
import argparse
import base64
import sys

#....

class PWAP8:
    def __init__(self):
        self.projectName = None
        self.projectNameShort = None
        self.srcHTML = None
        self.srcJS = None
        self.srcICON = None
        self.buildDir = None
        self.faviconStyle = "png"
        self.bInlineManifest = False

        self.iconSizes = [32, 128, 144, 152, 167, 180, 192, 256, 512]


    def _findPaths(self):
        #derived paths...

        if self.buildDir is None:
            self.buildDir = os.path.join(os.getcwd(), 'build')

        self.imagesDir = os.path.join(self.buildDir, 'images')

        self.srcHTML = os.path.abspath(self.srcHTML)
        self.srcJS = os.path.abspath(self.srcJS)

        (javaScriptDir, self.javascriptFile) = os.path.split(self.srcJS)


    def _createDirs(self):
        try:
            os.mkdir(self.buildDir)
        except OSError:
            pass

        try:
            os.mkdir(self.imagesDir)
        except OSError:
            pass


    def _tweakHTML(self, soup, manifest, swJS):
        #TODO: adding a DOCTYPE seems to mess with the finished game's layout, a browser issue?...
        #prefix with <!DOCTYPE html>...
        #doctype = Doctype('html')
        #soup.insert(0, doctype)

        #tweak head...
        head = soup.head

        #add some meta tags for colours, icons, etc...
        head.append(soup.new_tag('meta', attrs={'name': 'theme-color', 'content': 'white'}))
        head.append(soup.new_tag('meta', attrs={'name': 'apple-mobile-web-app-capable', 'content': 'yes'}))
        head.append(soup.new_tag('meta', attrs={'name': 'apple-mobile-web-app-status-bar-style', 'content':'black'}))
        head.append(soup.new_tag('meta', attrs={'name': 'apple-mobile-web-app-title', 'content':soup.title.string}))
        head.append(soup.new_tag('meta', attrs={'name': 'msapplication-TileImage', 'content':"images/{name}-icon-144.png".format(name=self.projectNameShort)}))
        head.append(soup.new_tag('meta', attrs={'name': 'msapplication-TileColor', 'content':'#FFFFFF'}))


        #favicons...
        head.append(soup.new_tag('link', attrs={'rel': 'apple-touch-icon', 'href': "images/{name}-icon-167.png.png".format(name=self.projectNameShort)}))

        if self.faviconStyle == "png":
            head.append(soup.new_tag('link', attrs={'rel':'icon', 'href':'favicon-32.png', 'type':'image/png'}))
        elif self.faviconStyle == "ico":
            head.append(soup.new_tag('link', attrs={'rel':'icon', 'href':'favicon.ico', 'type':'image/x-icon'}))


        #manifest...
        if self.bInlineManifest:
            manifestStr = json.dumps(manifest, indent=4, sort_keys=False)
            head.append(soup.new_tag('link', attrs={'rel':'manifest', 'href':'data:application/manifest+json,' + manifestStr}))
        else:
            head.append(soup.new_tag('link', attrs={'rel':'manifest', 'href':"{name}.manifest".format(name=self.projectNameShort)}))


        #tweak body...
        body = soup.body

        #something for when JavaScrript is off...
        fallbackContent = soup.new_tag("noscript")
        fallbackContent.string = "This will much be more fun with JavaScript enabled."
        body.append(fallbackContent)


        #service worker...
        #TODO: can we inline the service worker?...
        startSW = soup.new_tag("script", attrs={'type':'text/javascript'})
        startSW.string = "window.onload = () => { 'use strict'; if ('serviceWorker' in navigator) { navigator.serviceWorker.register('./sw.js');}}"
        body.append(startSW)


    def _createManifest(self):
        manifest = {
            'name': self.projectName,
            'short_name': self.projectNameShort,
            'start_url': '/index.html',
            'display': 'standalone',
            'theme_color': 'white',
            'background_color': 'white',
            'lang': 'en-US'
        }

        manifest['icons'] = []
        for size in self.iconSizes:
            icon = {'src': "images/{name}-icon-{size}.png".format(name=self.projectNameShort, size=size), 'sizes': "{size}x{size}".format(size=size), 'type': 'image/png'}
            manifest["icons"].append(icon)

        return manifest


    def _createServiceWorker(self, cachedThings):

        cachedStr = json.dumps(cachedThings)

        swJS = """//sw.js...
var cacheName = '{name}';

self.addEventListener('install', function(event) {{
    event.waitUntil(
    caches.open(cacheName).then(function(cache) {{ return cache.addAll({cached}); }})
    );
}});

self.addEventListener('fetch', function(event) {{
    event.respondWith(
    caches.match(event.request).then(function(response) {{ return response || fetch(event.request); }})
    );
}});

"""
        return swJS.format(name=self.projectName, cached=cachedStr)
    

    def _createIcon(self, sourceImage, size):
        icon = Image.new("RGBA", (size, size))

        thumb = sourceImage.copy()
        if thumb.width < 64:    #...TODO: remove hack
            method = Image.NEAREST
        else:
            method = Image.BICUBIC

        #scale up, then down to force thumbnail to work as expected...
        scale = 1024 / thumb.width
        thumb = thumb.resize((int(thumb.width * scale), int(thumb.height * scale)), method)
        thumb.thumbnail((size, size), method)
        #...TODO: this is a horrible hack, please fix

        offset = (size - thumb.width) / 2
        icon.paste(thumb, (int(offset), 0))

        return icon


    def _iconPath(self, pathFilename):
        (path, filename) = pathFilename

        if path is not None:
           logicalPath = os.path.join(path, filename)
        else:
            logicalPath = filename

        return os.path.join(self.buildDir, logicalPath)


    def _createIcons(self):
        iconFilenames = []

        #use the provided graphic, or use a default...
        if self.srcICON is not None:
            sourceImage = Image.open(self.srcICON)
        else:
            fallbackIconStr = 'Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_AAAAAAAAKa3_Ka3_Ka3_Ka3_Ka3_Ka3_AAAAAAAAKa3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_AAAAAAAAKa3_Ka3_Ka3_Ka3_Ka3_Ka3_AAAAAAAAKa3_Ka3_AAAAAAAAAAAAAAAAAAAAAAAAKa3_Ka3_AAAAAAAAAAAAAAAAAAAAAAAAKa3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_Ka3_'
            fallbackIconImage = Image.frombytes("RGB", (8, 8), base64.urlsafe_b64decode(fallbackIconStr))
            sourceImage = fallbackIconImage.copy()

        #resize and save each of the icons...
        for size in self.iconSizes:
            icon = self._createIcon(sourceImage, size)
            iconFilename = ('images', "{name}-icon-{size}.png".format(name=self.projectNameShort, size=size))
            icon.save(self._iconPath(iconFilename), "PNG")
            iconFilenames.append(iconFilename)

        #...and a favicon...
        if self.faviconStyle is not None:
            #additionally a classic 32 x 32 favicon referenced in the HTML...
            icon = self._createIcon(sourceImage, 32)
            if self.faviconStyle == "png":
                iconFilename = (None, 'favicon-32.png')
                icon.save(self._iconPath(iconFilename), "PNG")
                iconFilenames.append(iconFilename)
            elif self.faviconStyle == "ico":
                iconFilename = (None, 'favicon.ico')
                icon.save(self._iconPath(iconFilename), "ICO")
                iconFilenames.append(iconFilename)
        
        return iconFilenames


    def Run(self):
        print("Running build\n")
        
        self._findPaths()

        print("PROJECT_NAME = {name}".format(name=self.projectName))
        print("SHORT_NAME = {name}".format(name=self.projectNameShort))
        print("HTML = {html}".format(html=self.srcHTML))
        print("JAVASCRIPT = {js}".format(js=self.srcJS))
        print("ICON = {icon}".format(icon=self.srcICON))
        print("BUILD_DIR = {build}".format(build=self.buildDir))

        self._createDirs()

        #create manifest, icons, service worker...
        manifestFilename = "{name}.manifest".format(name=self.projectNameShort)

        manifest = self._createManifest()
        if not self.bInlineManifest:
            with open(os.path.join(self.buildDir, manifestFilename), "w") as fout:
                fout.write(json.dumps(manifest, indent=4, sort_keys=False))

        iconFilenames = self._createIcons()

        cachedThings = ['/', '/index.html', '/' + self.javascriptFile, '/sw.js', '/' + manifestFilename]
        for (path, filename) in iconFilenames:
            if path is not None:
                cachedThings.append("/{path}/{filename}".format(path = path, filename = filename))
            else:
                cachedThings.append('/' + filename)

        swJS = self._createServiceWorker(cachedThings)
        with open(os.path.join(self.buildDir, 'sw.js'), "w") as fout:
            fout.write(swJS)

        #open up the html exported from PICO-8...
        exportHML = None
        try:
            with open(self.srcHTML, "r") as fin:
                exportHML = fin.read()
        except OSError:
            print("\nERROR: unable to open exported HTML ({html})".format(html=self.srcJS))
            sys.exit()

        soup = BeautifulSoup(exportHML, 'html.parser')	#, from_encoding="utf-8")

        #mess with it...
        self._tweakHTML(soup, manifest, swJS)

        #write it out to the build dir...
        with open(os.path.join(self.buildDir, "index.html"), "w") as fout:
            fout.write(str(soup.prettify()))

        dstJS = os.path.join(self.buildDir, self.javascriptFile)

        try:
            shutil.copy(self.srcJS, dstJS)
        except OSError:
            print("\nERROR: unable to find exported JavaScript ({js})".format(js=self.srcJS))
            sys.exit()


#....



if __name__ == '__main__':
    print("""pwap8: A hack to add Progressive Web App elements to PICO-8 HTML exports
Copyright (c) 2020 Loxodromic
MIT License (see LICENSE)\n""")


    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--name', nargs=1, type=str, metavar='PROJECT_NAME', help='project name', required=True)
    parser.add_argument('--short', nargs=1, type=str, metavar='SHORT_NAME', help='short project name', required=False)
    parser.add_argument('--icon', nargs=1, type=str, metavar='<ICON>', help='an image to use for the icons', required=False)

    srcGroup = parser.add_argument_group('source')
    srcGroup.add_argument('--html', nargs=1, type=str, metavar='<EXPORT.html>', help='PICO-8 exported HTML', required=True)
    srcGroup.add_argument('--js', nargs=1, type=str, metavar='<JAVASCRIPT.js>', help='PICO-8 exported JavsScript', required=True)

    #TODO: intelligently determine html and JS filenames from just a dir...
    #srcGroup.add_argument('--dir', nargs=1, type=str, metavar='<DIRECTORY>', help='Directory containing PICO-8 exported HTML and JavaScript')

    dstGroup = parser.add_argument_group('destination')
    dstGroup.add_argument('--build', nargs=1, type=str, metavar='<BUILD_DIR>', help='Directory for build result (defaults to ./build)', required=False)
    
    args = parser.parse_args()

    pwap8 = PWAP8()
    pwap8.projectName = ''.join(args.name)
    pwap8.srcHTML = ''.join(args.html)
    pwap8.srcJS = ''.join(args.js)
    
    if args.icon is not None:
        pwap8.srcICON = ''.join(args.icon)

    pwap8.projectNameShort = pwap8.projectName
    if args.short is not None:
        pwap8.projectNameShort = ''.join(args.short)
   
    if args.build is not None:
        pwap8.buildDir = ''.join(args.build)

    pwap8.Run()

    print("\nEOL")

#....

