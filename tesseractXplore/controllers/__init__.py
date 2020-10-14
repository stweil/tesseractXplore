"""
Package for controller classes. The goal is to organize these such that each controller manages
the components & state from a single .kv file.
"""
from tesseractXplore.controllers.batch_loader import BatchLoader, TaxonBatchLoader, ImageBatchLoader
from tesseractXplore.controllers.controller import Controller
from tesseractXplore.controllers.image_selection_controller import ImageSelectionController
from tesseractXplore.controllers.metadata_view_controller import MetadataViewController
from tesseractXplore.controllers.observation_search_controller import ObservationSearchController
from tesseractXplore.controllers.settings_controller import SettingsController
from tesseractXplore.controllers.taxon_search_controller import TaxonSearchController
from tesseractXplore.controllers.taxon_selection_controller import TaxonSelectionController
from tesseractXplore.controllers.taxon_view_controller import TaxonViewController
