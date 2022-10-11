import dbdicom as db
import wezel


def all(parent):

    #parent.action(Copy, text='Copy', generation=0)
    #parent.action(Delete, text='Delete', generation=0)

    series = parent.menu('Series')
    series.action(Copy, text='Copy', generation=3)
    series.action(Delete, text='Delete', generation=3)
    series.action(Merge, text='Merge', generation=3)
    series.action(Group, text='Group', generation=3)
    series.separator()
    series.action(SeriesRename, text='Rename')
    series.action(SeriesExtract, text='Extract subseries')

    study = parent.menu('Study')
    study.action(Copy, text='Copy', generation=2)
    study.action(Delete, text='Delete', generation=2)
    study.action(Merge, text='Merge', generation=2)
    study.action(Group, text='Group', generation=2)

    patient = parent.menu('Patient')
    patient.action(Copy, text='Copy', generation=1)
    patient.action(Delete, text='Delete', generation=1)
    patient.action(Merge, text='Merge', generation=1)
    patient.action(Group, text='Group', generation=1)
    

class Copy(wezel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(self.generation) != 0

    def run(self, app):

        app.status.message("Copying..")
        records = app.get_selected(self.generation)        
        for j, record in enumerate(records):
            app.status.progress(j, len(records), 'Copying..')
            record.copy()               
        app.refresh()


class Delete(wezel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(self.generation) != 0

    def run(self, app):

        app.status.message("Deleting..")
        records = app.get_selected(self.generation)        
        for j, series in enumerate(records):
            app.status.progress(j, len(records), 'Deleting..')
            series.remove()               
        app.refresh()


class Merge(wezel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(self.generation) != 0

    def run(self, app): 

        app.status.message('Merging..')
        records = app.get_selected(self.generation)
        study = records[0].parent().new_sibling(StudyDescription='Merged Series')
        db.merge(records, study.new_series(SeriesDescription='Merged Series'))
        app.refresh()


class Group(wezel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(self.generation) != 0

    def run(self, app): 

        app.status.message('Merging..')
        records = app.get_selected(self.generation)
        study = records[0].parent().new_sibling(StudyDescription='Grouped Series')
        db.group(records, study)
        app.status.hide()
        app.refresh()


class SeriesRename(wezel.Action):

    def enable(self, app):
        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app): 
        series_list = app.get_selected(3)
        for s in series_list:
            cancel, f = app.dialog.input(
                {"type":"string", "label":"New series name:", "value": s.SeriesDescription},
                title = 'Enter new series name')
            if cancel:
                return
            s.SeriesDescription = f[0]['value']
        app.refresh()

class SeriesExtract(wezel.Action):

    def enable(self, app):

        if not hasattr(app, 'folder'):
            return False
        return app.nr_selected(3) != 0

    def run(self, app):

        # Get source data
        series = app.get_selected(3)[0]
        _, slices = series.get_pixel_array(['SliceLocation', 'AcquisitionTime'])
        nz, nt = slices.shape[0], slices.shape[1]
        x0, x1, t0, t1 = 0, nz, 0, nt

        # Get user input
        invalid = True
        while invalid:
            cancel, f = app.dialog.input(
                {"type":"integer", "label":"Slice location from index..", "value":x0, "minimum": 0, "maximum": nz},
                {"type":"integer", "label":"Slice location to index..", "value":x1, "minimum": 0, "maximum": nz},
                {"type":"integer", "label":"Acquisition time from index..", "value":t0, "minimum": 0, "maximum": nt},
                {"type":"integer", "label":"Acquisition time to index..", "value":t1, "minimum": 0, "maximum": nt},
                title='Select parameter ranges')
            if cancel: 
                return
            x0, x1, t0, t1 = f[0]['value'], f[1]['value'], f[2]['value'], f[3]['value']
            invalid = (x0 >= x1) or (t0 >= t1)
            if invalid:
                app.dialog.information("Invalid selection - first index must be lower than second")

        # Extract series and save
        study = series.parent().new_sibling(StudyDescription='Extracted Series')
        indices = ' [' + str(x0) + ':' + str(x1) 
        indices += ', ' + str(t0) + ':' + str(t1) + ']'
        new_series = study.new_child(SeriesDescription = series.SeriesDescription + indices)
        db.copy_to(slices[x0:x1,t0:t1,:], new_series)
        app.refresh()