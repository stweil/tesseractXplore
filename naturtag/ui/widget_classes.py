""" Stub classes for custom widgets and screens """
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.button import MDRoundFlatIconButton
from kivymd.uix.list import ILeftBodyTouch, IRightBodyTouch, OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextFieldRound
from kivymd.uix.tooltip import MDTooltip


# Screen classes
class ImageSelectorScreen(MDScreen):
    pass

class SettingsScreen(MDScreen):
    pass

class MetadataViewScreen(MDScreen):
    pass

class TaxonSearchScreen(MDScreen):
    pass

class ObservationSearchScreen(MDScreen):
    pass


HOME_SCREEN = 'image_selector'
SCREENS = {
    HOME_SCREEN: ImageSelectorScreen,
    'settings': SettingsScreen,
    'metadata': MetadataViewScreen,
    'taxon_search': TaxonSearchScreen,
    'observation_search': ObservationSearchScreen,
}


# Controls & other UI elements
class SwitchListItem(ILeftBodyTouch, MDSwitch):
    """ Switch that works as a list item """

class TextInputListItem(OneLineListItem, MDTextFieldRound):
    """ Switch that works as a list item """

class TooltipFloatingButton(MDFloatingActionButton, MDTooltip):
    """ Floating action button class with tooltip behavior """

class TooltipIconButton(MDRoundFlatIconButton, MDTooltip):
    """ Flat button class with icon and tooltip behavior """

class MetadataTab(BoxLayout, MDTabsBase):
    """ Class for a tab in a MDTabs view"""