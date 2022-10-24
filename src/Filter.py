from src.filterstage import *
from src.designconfiguration import *
from src.filterdesign import *

class Filter:
    def __init__(self, filter_design = FilterDesign(), designconfig = DesignConfig(), filter_stages = dict(), editingStage = False, editingStageIndex = 0, current_template = 0, gain_remaining = 0, orden = 0, visible = True):
        self.filter_design = filter_design
        self.designconfig = designconfig
        self.filter_stages = filter_stages
        self.editingStage = editingStage
        self.editingStageIndex = editingStageIndex
        self.current_template = current_template
        self.gain_remaining = gain_remaining
        self.orden = orden
        self.visible = visible