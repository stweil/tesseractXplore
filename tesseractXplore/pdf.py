from kivymd.uix.list import MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem, OneLineAvatarListItem
from kivymd.uix.dropdownitem import MDDropDownItem
from tesseractXplore.widgets.lists import SwitchListItem
from tesseractXplore.app import alert
from tesseractXplore.controllers.fulltext_view_controller import find_file
from functools import partial
from subprocess import Popen
from os import makedirs
from pathlib import Path
from subprocess import getstatusoutput, check_output
from sys import platform as _platform
from kivymd.toast import toast
from logging import getLogger

from tesseractXplore.constants import PDF_DIR

import threading
from tesseractXplore.app import get_app

logger = getLogger().getChild(__name__)

def pdf_dialog(pdfpath):
    # Called by image_glob.py
    def close_dialog(instance, *args):
        instance.parent.parent.parent.parent.dismiss()
    layout = MDList()
    if getstatusoutput("pdfimages")[0] != 127:
        import re
        pdfinfos = check_output(["pdfimages","-list", pdfpath]).decode('utf-8')
        pdfinfos = re.sub(r' +', ' ', pdfinfos)
        pdfinfos = pdfinfos.split("\n")[2:-1]
        pages = str(len(pdfinfos))
        dpis = [pdfinfo.split(" ")[-3] for pdfinfo in pdfinfos]
        from collections import Counter
        dpi = Counter(dpis).most_common(1)[0][0]
    else:
        pages = ""
    layout.add_widget(OneLineListItem(text=f'The detected resolution is: {dpi}'))
    layout.add_widget(OneLineListItem( text='First page'))
    layout.add_widget(MDTextField(id="first", text="0", hint_text="First page", height=400))
    layout.add_widget(OneLineListItem(text='Last page'))
    layout.add_widget(MDTextField(id="last", text=pages, hint_text="Last page",height=400))
    layout.add_widget(OneLineListItem(text='Imageformat (jpg, jp2, png, ppm(default), tiff)'))

    from kivymd.uix.boxlayout import MDBoxLayout
    from tesseractXplore.widgets import MyToggleButton
    boxlayout = MDBoxLayout(id="fileformat",orientation="horizontal", adaptive_height=True)
    boxlayout.add_widget(MyToggleButton(text="jpg",group="imageformat"))
    boxlayout.add_widget(MyToggleButton(text="jp2", group="imageformat"))
    defaulttoggle =  MyToggleButton(text="ppm", group="imageformat")
    boxlayout.add_widget(defaulttoggle)
    boxlayout.add_widget(MyToggleButton(text="png", group="imageformat"))
    boxlayout.add_widget(MyToggleButton(text="tiff", group="imageformat"))
    layout.add_widget(boxlayout)
    #layout.add_widget(MDTextField(id="fileformat", text="jpg", hint_text="Fileformat", height=400))
    pagenumbers = OneLineAvatarListItem(id='include_pagenumber',text='Include page numbers in output file names')
    pagenumbers.add_widget(SwitchListItem(id='include_pagenumber_chk'))
    layout.add_widget(pagenumbers)
    dialog = MDDialog(title="Extract images from PDF",
                         type='custom',
                         auto_dismiss=False,
                         text=pdfpath,
                         content_cls=layout,
                         buttons=[
                             MDFlatButton(
                                 text="CREATE IMAGES", on_release=partial(pdfimages_threading, pdfpath)
                             ),
                             MDFlatButton(
                                 text="VIEW PDF", on_release=partial(open_pdf, pdfpath)
                             ),
                            MDFlatButton(
                                text="DISCARD", on_release=close_dialog
                            ),
                        ],
                    )
    defaulttoggle.state = 'down'
    dialog.content_cls.focused = True
    dialog.open()


def pdfimages_threading(pdfpath, instance,*args):
    instance.parent.parent.parent.parent.dismiss()
    pdfimages_thread = threading.Thread(target=pdfimages, args=(pdfpath, instance,args))
    pdfimages_thread.setDaemon(True)
    pdfimages_thread.start()

def open_pdf(fname, *args):
    """ Open a pdf via webbrowser or another external software """
    pdfviewer = get_app().settings_controller.pdfviewer
    if pdfviewer == 'webbrowser':
        import webbrowser
        webbrowser.open(str(Path(fname).absolute()))
    else:
        import subprocess
        try:
            subprocess.run([pdfviewer, str(Path(fname).absolute())])
        except:
            alert(f"Couldn't find: {pdfviewer}")
            pass

def pdfimages(pdfpath, instance, *args):
    from tesseractXplore.widgets.progressbar import MDProgressBar
    pb = MDProgressBar(color=get_app().theme_cls.primary_color,type="indeterminate")
    status_bar = get_app().image_selection_controller.status_bar
    status_bar.clear_widgets()
    status_bar.add_widget(pb)
    pb.start()
    pdfdir = Path(pdfpath.split('.')[0])
    makedirs(pdfdir, exist_ok=True)
    params = []
    children =  instance.parent.parent.parent.parent.content_cls.children
    for child in children:
        if child.id == "fileformat":
            for fileformat in child.children:
                if fileformat.state == 'down':
                    fileformat.text = "j" if fileformat.text == "jpg" else fileformat.text
                    params.extend([f"-{fileformat.text}"])
        if child.id == "first" and child.text != "":
            params.extend(["-f", child.text])
        if child.id == "last" and child.text != "":
            params.extend(["-l", child.text])
        if child.id == "include_pagenumber" and child.ids['_left_container'].children[0].active:
            params.extend(["-p"])
    p1 = Popen(["pdfimages", *params, pdfpath, pdfdir.joinpath(pdfdir.name)])
    p1.communicate()
    get_app().image_selection_controller.file_chooser._update_files()
    get_app().image_selection_controller.add_images([pdfdir])
    pb.stop()

def extract_pdf(pdfpath):
    if _platform not in ["win32", "win64"]:
        if getstatusoutput("pdfimages")[0] != 127:
            pdf_dialog(pdfpath)
            return pdfpath.split(".")[0]
        else:
            toast("Please install poppler-utils to work with pdf")
    else:
        pdftoolpath = Path(PDF_DIR)
        if not pdftoolpath.exists():
            # TODO: Don work atm properly and use the official site
            url = 'https://digi.bib.uni-mannheim.de/~jkamlah/poppler-20.12.1-h7cbfaf2_0.tar.bz2'
            try:
                pass
                #import requests, zipfile, io
                #r = requests.get(url, stream=True)
                #pdftoolpath.mkdir(parents=True)
                #z = zipfile.ZipFile(io.BytesIO(r.content))
                #z.extractall(str(pdftoolpath.absolute()))
                #logger.info(f'Download: Succesful')
                # Update Modelslist
                #get_app().tesseract_controller.models = get_app().tesseract_controller.get_models()
            except:
                logger.info(f'Download: Error while downloading')
    return pdfpath