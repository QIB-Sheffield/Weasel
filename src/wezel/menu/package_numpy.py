import wezel
from dbdicom.wrappers import numpy


def all(parent):   
    parent.action(ThresholdAbsolute, text="Threshold (absolute values)")
    parent.action(ThresholdRelative, text="Threshold (relative values)")



class ThresholdAbsolute(wezel.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):

        # Get user input
        cancel, f = app.dialog.input(
            {"label":"low threshold (signal units)", "type":"float", "value": 0},
            {"label":"high threshold (signal units)", "type":"float", "value": 100},
            title = 'Select Thresholding settings')
        if cancel: 
            return

        # Filter series
        series = app.selected('Series')
        for sery in series:
            filtered = numpy.threshold(
                sery, 
                low_threshold = f[0]['value'],
                high_threshold = f[1]['value'],
                method = 'absolute',
            )
            app.display(filtered)
        app.refresh()


class ThresholdRelative(wezel.Action): 

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):

        # Get user input
        cancel, f = app.dialog.input(
            {"label":"low threshold (%)", "type":"float", "value": 25.0, "minimum": 0.0, 'maximum':100.0},
            {"label":"high threshold (%)", "type":"float", "value": 75.0, "minimum": 0.0, 'maximum':100.0},
            {"label":"thresholding method", "type":"dropdownlist", "list": ['Range', 'Percentile'], "value": 1},
            title = 'Select Thresholding settings')
        if cancel: 
            return
        if f[2]['value'] == 1:
            method = 'quantiles'
        else:
            method = 'range'

        # Filter series
        series = app.selected('Series')
        for sery in series:
            filtered = numpy.threshold(
                sery, 
                low_threshold = f[0]['value']/100,
                high_threshold = f[1]['value']/100,
                method = method,
            )
            app.display(filtered)
        app.refresh()
