import logging
import os
import sys
from os.path import dirname, join
os.environ['KIVY_GL_BACKEND'] = 'sdl2'

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import DictProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp as App
from kivymd.uix.imagelist import SmartTileWithLabel as ImageTile
from kivymd.uix.snackbar import Snackbar

from kv.widgets import SCREENS
from naturtag.app import tag_images

logger = logging.getLogger(__name__)
logger.setLevel('INFO')
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('[%(levelname)s] %(funcName)s %(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
logger.addHandler(out_hdlr)

ASSETS_DIR = join(dirname(dirname(__file__)), 'assets', '')
KV_SRC_DIR = join(dirname(dirname(__file__)), 'kv')
IMAGE_FILETYPES = ['*.jpg', '*.jpeg', '*.png', '*.gif']
INIT_WINDOW_SIZE = (1250, 800)
MD_PRIMARY_PALETTE = 'Teal'
MD_ACCENT_PALETTE = 'Cyan'


class Metadata(Widget):
    exif = DictProperty({})
    iptc = DictProperty({})
    xmp = DictProperty({})


class Controller(BoxLayout):
    file_list = ListProperty([])
    file_list_text = StringProperty()
    selected_image_table = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize screens and store references to them
        for name, cls in SCREENS.items():
            Builder.load_file(join(KV_SRC_DIR, f'{name}.kv'))
            new_screen = cls()
            new_screen.controller = self
            self.ids.screen_manager.add_widget(new_screen)
            self.__setattr__(f'{name}_screen', new_screen)

        # Add additional references to some nested objects for easier access
        self.settings = self.settings_screen.ids
        self.inputs = self.image_selector_screen.ids
        self.image_previews = self.image_selector_screen.ids.image_previews
        self.file_chooser = self.image_selector_screen.ids.file_chooser

        # Automatically adjust image preview layout
        self.image_previews.bind(minimum_height=self.image_previews.setter('height'))

    def add_image(self, window=None, path=None):
        """ Add an image to the current selection, with deduplication """
        if isinstance(path, bytes):
            path = path.decode('utf-8')

        if path not in self.file_list:
            # Update file list
            logger.info(f'Adding image: {path}')
            self.file_list.append(path)
            self.file_list.sort()
            self.inputs.file_list_text_box.text = '\n'.join(self.file_list)
            # Update image previews
            img = ImageTile(source=path)
            img.bind(on_release=self.remove_image)
            self.image_previews.add_widget(img)

    def add_images(self, paths):
        """ Add one or more files selected via a FileChooser """
        for path in paths:
            self.add_image(path=path)

    def remove_image(self, image):
        """ Remove an image from file list and image previews """
        self.file_list.remove(image.source)
        self.inputs.file_list_text_box.text = '\n'.join(self.file_list)
        image.parent.remove_widget(image)

    # TODO: Apply image file glob patterns to dir
    def add_dir_selection(self, dir):
        print(dir)

    def get_settings_dict(self):
        return {
            'common_names': self.settings.common_names_chk.active,
            'hierarchical_keywords': self.settings.hierarchical_keywords_chk.active,
            'darwin_core': self.settings.darwin_core_chk.active,
            'create_xmp': self.settings.create_xmp_chk.active,
            'dark_mode': self.settings.dark_mode_chk.active,
            "observation_id": int(self.inputs.observation_id_input.text or 0),
            "taxon_id": int(self.inputs.taxon_id_input.text or 0),
        }

    def get_state(self):
        logger.info(
            f'IDs: {self.ids}\n'
            f'Files:\n{self.file_list_text}\n'
            f'Config: {self.get_settings_dict()}\n'
        )

    def reset(self):
        """ Clear all image selections """
        logger.info('Clearing image selections')
        self.file_list = []
        self.file_list_text = ''
        self.file_chooser.selection = []
        self.image_previews.clear_widgets()

    def run(self):
        """ Run image tagging for selected images and input """
        settings = self.get_settings_dict()
        tag_images(
            settings['observation_id'],
            settings['taxon_id'],
            settings['common_names'],
            settings['hierarchical_keywords'],
            settings['create_xmp'],
            self.file_list,
        )


class ImageTaggerApp(App):
    def build(self):
        Builder.load_file(join(KV_SRC_DIR, 'main.kv'))

        # Window and theme settings
        controller = Controller()
        Window.bind(on_dropfile=controller.add_image)
        Window.size = INIT_WINDOW_SIZE
        self.theme_cls.primary_palette = MD_PRIMARY_PALETTE
        self.theme_cls.accent_palette = MD_ACCENT_PALETTE
        controller.settings.dark_mode_chk.bind(active=self.toggle_dark_mode)

        controller.ids.screen_manager.current = 'image_selector'
        # controller.ids.screen_manager.current = 'settings'
        Snackbar(
            text=f'.{" " * 14}Drag and drop images or select them from the file chooser',
            duration=10
        ).show()
        return controller

    def toggle_dark_mode(self, switch=None, is_active=False):
        self.theme_cls.theme_style = 'Dark' if is_active else 'Light'


if __name__ == '__main__':
    ImageTaggerApp().run()