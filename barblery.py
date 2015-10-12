#!/usr/bin/env python
###########################################################################
#                          :$RCSfile: barblery.py,v $:  -  description                         
#                             -------------------
#    begin                : gio mag 19 17:35:30 Europe/Rome 2005
#    copyright            : (C) 2005 by Andrea Gangemi
#    email                : a.gangemi@cheapnet.it
###########################################################################

###########################################################################
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#   see COPYING for further details                                       #
###########################################################################

import os
import sys
import commands
import shutil
import code
from optparse import OptionParser
from time import gmtime, strftime

__version__ = "1.0"


def immagina(options, dove, previous):
    # change directory
        # todo metti un uscita piu elegante
    # if not os.chdir(dove):
    #    print " Error: Directory "+dove+" not exists"
    #    sys.exit(-2)
    os.chdir(dove)
    # qui=os.getcwd()
    if options.verbose:
        print ' now processing: %s' % os.getcwd()
    # create .thumb directory if doesn't exists
    if os.path.isdir('.thumbs'):
        shutil.rmtree('.thumbs')
    os.mkdir('.thumbs')
    # if options.verbose:
    # print ' creating .barblery subdir and copying some data'
    # copy button and logo image inside .barblery dir
    if os.path.isdir('.barblery'):
        shutil.rmtree('.barblery')
    os.mkdir('.barblery')
    if options.show_buttons:
        commands.getstatusoutput('cp ' + options.data_dir + '/back_button.png .barblery')
        commands.getstatusoutput('cp ' + options.data_dir + '/up_button.png .barblery')
    commands.getstatusoutput('cp ' + options.data_dir + '/barblery_logo.png .barblery')

    # create images.html file
    # print 'data dir',options.data_dir
    templatefile = open(options.data_dir + '/barblery_template.html', 'r')
    tempstr = templatefile.read()
    templatefile.close()

    # copies a stylesheet if it doesn't exists
    make_stylesheet(options)

    # make title and header
    titolo = options.title + ' ' + os.path.basename(dove.strip('/'))
    tempstr = make_html_title(titolo, tempstr)

    # make body

    # header
    tempstr = make_html_header(titolo, tempstr, options, previous)
    # description
    tempstr = make_html_description(tempstr, options.verbose)
    # directories & images
    files, tempstr = make_html_contents(tempstr, options)

    # make trailer
    tempstr = make_html_trailer(tempstr)

    # write images.html
    htmlfile = open('images.html', 'w')
    htmlfile.write(tempstr)
    htmlfile.close()
    templatefile.close()

    return files


def make_html_title(titolo, tempstr):
    """ Creates HTML title """
    tempstr = tempstr.replace('<!-- barblerytemplate_title -->', titolo)
    return tempstr


def make_html_header(titolo, tempstr, options, prev):
    """ Creates HTML header """
    tempstr = tempstr.replace('<!-- barblerytemplate_header -->', '\
    <h1>' + titolo + '</h1>\n')
    if options.show_buttons:
        btn_str = '<a href="' + options.btn_root_url + '">' + \
                  '<img src=".barblery/up_button.png" hspace=8 vspace=8 border="0" alt="Root"></a>\n'
        if options.btn_back_url != '':
            btn_str = btn_str + '<a href="' + options.btn_back_url + '/images.html">' + \
                '<img src=".barblery/back_button.png" hspace=8 vspace=8 border="0"alt="Back"></a>\n</br>\n'
        else:
            if prev != '':
                btn_str = btn_str + '<a href="' + prev + '/images.html">' + \
                    '<img src=".barblery/back_button.png" hspace=8 vspace=8 border="0"alt="Back"></a>\n</br>\n'
        tempstr = tempstr.replace('<!-- barblerytemplate_buttons -->', btn_str)
    return tempstr


def make_html_description(tempstr, verbose):
    """ put the contents of description.txt if found """
    descstr = ''
    if os.path.isfile('description.txt'):
        if verbose:
            print ' found description.txt'
        descriptionfile = open('description.txt', 'r')
        # now conver a .txt file into an HTML syntax
        descstr = '<h3>'
        desc_list = descriptionfile.readlines()
        for descline in desc_list:
            descstr = descstr + descline + '</br>\n'
        descstr += '</h3>\n'
        descriptionfile.close()
        # replace special chars
    return tempstr.replace('<!-- barblerytemplate_description -->', descstr)


def make_html_contents(tempstr, options):
    """ put directories and images listing """

    # generate directory list
    qui = os.getcwd()
    dirfiles = 0
    dir_string = ''
    # this is the Big Trick, thanks to Davide and Python
    # dirs contains a list of directories except the ones beginning with a dot
    dirs = [x for x in os.listdir('.') if os.path.isdir(x) and x[0] != '.']
    if len(dirs) > 0:
        dir_string = 'Subdirectories [' + str(len(dirs)) + ']:</br>\n'
        end_dir_string = '<hr width="100%">\n'
    else:
        dir_string = ''
        end_dir_string = '\n'
    dirs.sort()

    for x in dirs:
        img_number = immagina(options, x, qui)
        dirfiles += img_number
        os.chdir(qui)
        dir_string = dir_string + '<a href="' + x + '/images.html"> ' + x + ' [' + str(img_number) + ']</a></br>\n'
    dir_string += end_dir_string
    tempstr = tempstr.replace('<!-- barblerytemplate_directories -->', dir_string)

    # generate thumbnails
    if options.verbose:
        print ' Generating image gallery'
        print ' [mumble mumble]...'
    jpg_list = [x for x in os.listdir(".")
                if os.path.isfile(x) and not
                commands.getstatusoutput('convert -resize ' +
                                         options.geometry + ' "' +
                                         x + '" ".thumbs/' +
                                         x + '"')[0]]
    img_number = len(jpg_list)
    if options.verbose:
        print ' ' + str(img_number) + ' thumbs created:'
        print ' ', jpg_list
    if img_number > 0:
        jpg_string = 'Images:</br>\n'
        end_jpg_string = '<hr width="100%">\n'
        jpg_string += '<table>\n<tr>\n'
    else:
        jpg_string = ''
        end_jpg_string = '\n'

    # put image link
    imgcount = 0
    for x in jpg_list[:]:
        if imgcount >= options.img_per_row:
            imgcount = 0
            jpg_string += '</tr>\n<tr>\n'
        imgcount += 1
        # print '%c' % '.'
        jpg_string += '<td align="center">'
        jpg_string += '<a href="' + x + '">'
        jpg_string += '<img src=".thumbs/' + x + '" hspace=8 vspace=8 '
        jpg_string += 'alt="' + os.path.splitext(x)[0] + '" align="top">'
        if options.show_caption:
            jpg_string = jpg_string + '<div>' + os.path.splitext(x)[0] + '</div>'
        jpg_string += '</a>\n</td>'
    if img_number > 0:
        jpg_string += '</tr>\n</table>\n'
    jpg_string += end_jpg_string
    tempstr = tempstr.replace('<!-- barblerytemplate_images -->', jpg_string)

    return (dirfiles + img_number), tempstr


def make_html_trailer(tempstr):
    """ Create HTML trailer """

    trailerstr = """
    <h6>Generated by <a href="http://harzack.freeshell.org/barblery.html"><img src=".barblery/barblery_logo.png"
    alt="Barblery" align="middle" border="0"></a> Ver. 1.00 on """
    trailerstr = trailerstr + strftime("%d-%m-%y. %H:%M:%S", gmtime()) + '</h6>'
    tempstr = tempstr.replace('<!-- barblerytemplate_trailer -->', trailerstr)
    return tempstr


def make_stylesheet(options):
    """ Creates a default stylesheet """
    if not os.path.isfile(options.css_filename) or options.rebuild_css:
        commands.getstatusoutput('cp ' + options.data_dir + '/' + options.css_filename + ' .')

    return


def main():

    data_dir = os.getenv("HOME", 0) + '/.barblery_data'

    usage = "usage: %prog [options] root_directory"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                      action="store_true", 
                      dest="verbose",
                      default=True,
                      help="verbose mode ON [default]")
    parser.add_option("-q", "--quiet",
                      action="store_false", 
                      dest="verbose",
                      help="run silent")
    parser.add_option("-d", "--data-dir",
                      action="store",
                      dest="data_dir",
                      default=data_dir,
                      help="data directory ["+data_dir+"]")
    parser.add_option("-t", "--title",
                      action="store",
                      dest="title",
                      default="Barblery for: ",
                      help="set HTML title to TITLE")
    parser.add_option("-s", "--show-buttons",
                      action="store_true",
                      dest="show_buttons",
                      default=False,
                      help="show navigation buttons on page")
    parser.add_option("-r", "--root_url",
                      action="store",
                      dest="btn_root_url",
                      default="",
                      help="root button URL [root_directory]")
    parser.add_option("-b", "--back_url",
                      action="store",
                      dest="btn_back_url",
                      default="",
                      help="back button URL [root_directory]")
    parser.add_option("-n", "--image-per-row",
                      action="store",
                      type="int",
                      dest="img_per_row",
                      default=5,
                      help="put n images in a row [5]")
    parser.add_option("-i", "--image-caption",
                      action="store_true",
                      dest="show_caption",
                      default=False,
                      help="show image filename as caption")
    parser.add_option("--rebuild_css",
                      action="store_true",
                      dest="rebuild_css",
                      default=False,
                      help="overwrite CSS file if found")
    parser.add_option("-c", "--css_file",
                      action="store",
                      dest="css_filename",
                      default="barblery.css",
                      help="use different stylesheet")
    parser.add_option("-g", "--geometry",
                      action="store",
                      dest="geometry",
                      default="120x120",
                      help="thumbnails dimension [120x120]")
    # [...]
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    if options.verbose:
        print ' '
        print ' Hi, this is Barblery ' + __version__ + ' 8-)'
        print ' Written by Andrea Gangemi: http://harzack.freeshell.org '
        print ' '
        print ' REMEMBER: BARBLERY COMES WITHOUT WARRANTY OF ANY KIND '
        print ' '
        print ' I\'m gonna entering recursively your dirs looking for images'
        print ' starting from ' + args[0]
    immagina(options, args[0], '')
    return

if __name__ == "__main__":
    main()
