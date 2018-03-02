from PyQt4.QtCore import *
from qgis.analysis import * 
from os.path import join


####################           setup     #########################
####las capas necesitan estar en UTM y tener un identificador ejemplo "ageb_id"
folder = "/Users/fidel/Dropbox (LNCS)/banco_datos/encharcamientos_agebs/"
new_geom = QgsVectorLayer("/Users/fidel/Dropbox (LNCS)/banco_datos/encharcamientos_agebs/agebs_input.shp", "new_geom", "ogr")
new_geom_id = "ageb_id"
old_geom = QgsVectorLayer("/Users/fidel/Dropbox (LNCS)/banco_datos/encharcamientos_agebs/colonias_encharcamientos_1014_utm.shp", "old_geom", "ogr")
old_geom_id = "col_id"
resamplingFields = ["Frecuencia","proba"]
########################################################

print "calculando areas..."
new_geom.dataProvider().addAttributes([QgsField("area_new", QVariant.Double)])
new_geom.updateFields()
new_geom.startEditing()
for poligono in new_geom.getFeatures():
    poligono["area_new"] = poligono.geometry().area() 
    new_geom.updateFeature(poligono)
new_geom.commitChanges()

old_geom.dataProvider().addAttributes([QgsField("area_old", QVariant.Double)])
old_geom.updateFields()
old_geom.startEditing()
for poligono in old_geom.getFeatures():
    poligono["area_old"] = poligono.geometry().area() 
    old_geom.updateFeature(poligono)
old_geom.commitChanges()


print "intersectando..."

QgsOverlayAnalyzer().intersection(new_geom, old_geom, join(folder,"inter_temp.shp")) 

intersection = QgsVectorLayer(join(folder,"inter_temp.shp"), "intersection", "ogr")
intersection.dataProvider().addAttributes([QgsField("area_bit", QVariant.Double)])
intersection.updateFields()
intersection.startEditing()
for poligono in intersection.getFeatures():
    poligono["area_bit"] = poligono.geometry().area() 
    intersection.updateFeature(poligono)
intersection.commitChanges()


for resamplingField in resamplingFields:
        new_geom.dataProvider().addAttributes([QgsField(resamplingField, QVariant.Double)])
        new_geom.updateFields()


new_geom.startEditing()
for poligono in new_geom.getFeatures():
    
    print "procesando el poligono", poligono[new_geom_id], ":"
    for resamplingField in resamplingFields:
        
        new_field_value = 0.0
        for bit in intersection.getFeatures():
            if (int(bit[new_geom_id]) == int(poligono[new_geom_id])):
                new_field_value += (bit["area_bit"] / bit["area_old"]) * float(bit[resamplingField])
            
        poligono[resamplingField] = new_field_value
        new_geom.updateFeature(poligono)
    
new_geom.commitChanges()
    