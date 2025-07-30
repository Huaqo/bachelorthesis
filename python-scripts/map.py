from qgis.core import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *
from datetime import datetime
import os

QGIS_PREFIX_PATH = "/Applications/QGIS.app/Contents/Resources/python"
LAYER_PATH = "/Users/huaqo/Developer/courses/2024_Remote_Sensing/lab6/stacked/stacked.tif"
STYLE_PATH = "/Users/huaqo/Developer/courses/2024_Remote_Sensing/styles/true_color_2.qml"  
EXPORT_PATH = "/Users/huaqo/Developer/courses/2024_Remote_Sensing/lab6/maps/true_color_water.png"  
NORTH_ARROW_PATH = "/Users/huaqo/Developer/courses/2024_Remote_Sensing/styles/north_arrow.svg"

SECOND_LAYER_PATH = "/Users/huaqo/Developer/courses/2024_Remote_Sensing/lab6/kmeans/kmeans_5.tif"
STYLE_PATH_SECOND = "/Users/huaqo/Developer/courses/2024_Remote_Sensing/styles/overlay_water.qml"

map_pos_x = 20
map_pos_y = 30
map_size_x = 200
map_size_y = 150

grid_interval_x = 100000
grid_interval_y = 100000

LAYER_NAME = "True Color"
SECOND_LAYER_NAME = "Water"

legend_pos_x = 245
legend_pos_y = 30

scalebar_pos_x = 20
scalebar_pos_y = 190

north_arrow_pos_x = 30
north_arrow_pos_y = 40
north_arrow_size_x = 15
north_arrow_size_y = 15

title_text = "True Color Landsat and K-means Water class"
title_fontsize = 16
title_height = 10

author_text = "Author: Joaquin Gottlebe"
author_pos_y = 100

date_text = f"Date: {datetime.now().strftime('%d.%m.%Y')}"
date_pos_y = 110

crs_text = "CRS: EPSG 32633"
crs_pos_y = 120

fontfamily = "Arial"
info_font_size = 12
info_pos_x = legend_pos_x

# Initialize QGIS Application
QgsApplication.setPrefixPath(QGIS_PREFIX_PATH, True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Cleanup
project = QgsProject.instance()
layer_ids = list(project.mapLayers().keys())
for layer_id in layer_ids:
    project.removeMapLayer(layer_id)

# Load Layer
raster_layer = QgsRasterLayer(LAYER_PATH, LAYER_NAME)
if not raster_layer.isValid():
    raise Exception(f"{LAYER_NAME} layer failed to load!")

second_raster_layer = QgsRasterLayer(SECOND_LAYER_PATH, SECOND_LAYER_NAME)
if not second_raster_layer.isValid():
    raise Exception(f"{SECOND_LAYER_NAME} layer failed to load!")


QgsProject.instance().addMapLayer(raster_layer)
if not raster_layer.loadNamedStyle(STYLE_PATH):
    raise Exception(f"Style {STYLE_PATH} failed to load")

QgsProject.instance().addMapLayer(second_raster_layer)
if not second_raster_layer.loadNamedStyle(STYLE_PATH_SECOND):
    raise Exception(f"Style {STYLE_PATH_SECOND} failed to load")

# Create Layout
layout = QgsPrintLayout(project)
layout.initializeDefaults()

# Map
map_item = QgsLayoutItemMap(layout)
map_item.attemptMove(QgsLayoutPoint(map_pos_x,map_pos_y, QgsUnitTypes.LayoutMillimeters))
map_item.attemptResize(QgsLayoutSize(map_size_x, map_size_y, QgsUnitTypes.LayoutMillimeters))
map_item.zoomToExtent(raster_layer.extent())
layout.addLayoutItem(map_item)

# Add Coordinate Grid
grid = map_item.grid()
grid.setEnabled(True)
grid.setIntervalX(grid_interval_x)
grid.setIntervalY(grid_interval_y)
grid.setAnnotationEnabled(True)
grid.setAnnotationPrecision(0)
grid.setFrameStyle(QgsLayoutItemMapGrid.Zebra)

# Label
title_label = QgsLayoutItemLabel(layout)
title_label.setText(title_text)
title_label.setFont(QFont(fontfamily, title_fontsize))
title_label.setHAlign(Qt.AlignCenter)
title_label.adjustSizeToText()
layout_width = layout.pageCollection().page(0).pageSize().width()
title_width = title_label.rectWithFrame().width()
center_x = (layout_width - title_width) / 2
title_label.attemptMove(QgsLayoutPoint(center_x, title_height, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(title_label)

# Legend
legend_item = QgsLayoutItemLegend(layout)
legend_item.setLinkedMap(map_item)
legend_item.setTitle("Legend")
legend_item.setFrameEnabled(True)
legend_item.attemptMove(QgsLayoutPoint(legend_pos_x,legend_pos_y, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(legend_item)

# Scalebar
scalebar_item = QgsLayoutItemScaleBar(layout)
scalebar_item.setStyle('Single Box')
scalebar_item.setLinkedMap(map_item)
scalebar_item.setUnitLabel('m')
scalebar_item.setNumberOfSegments(4)
scalebar_item.setNumberOfSegmentsLeft(0)
scalebar_item.setUnitsPerSegment(50000)
scalebar_item.applyDefaultSize()
scalebar_item.attemptMove(QgsLayoutPoint(scalebar_pos_x,scalebar_pos_y, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(scalebar_item)

# North Arrow
north_arrow_item = QgsLayoutItemPicture(layout)
north_arrow_item.setPicturePath(NORTH_ARROW_PATH)
if not north_arrow_item.picturePath():
    print("North arrow image failed to load!")
north_arrow_item.setReferencePoint(QgsLayoutItemPicture.UpperLeft)
north_arrow_item.attemptMove(QgsLayoutPoint(north_arrow_pos_x,north_arrow_pos_y,QgsUnitTypes.LayoutMillimeters))
north_arrow_item.attemptResize(QgsLayoutSize(north_arrow_size_x,north_arrow_size_y,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(north_arrow_item)

# Author Info
info_label = QgsLayoutItemLabel(layout)
info_label.setText(author_text)
info_label.setFont(QFont(fontfamily, info_font_size))
info_label.setHAlign(Qt.AlignLeft)
info_label.attemptMove(QgsLayoutPoint(info_pos_x, author_pos_y, QgsUnitTypes.LayoutMillimeters))
info_label.adjustSizeToText()
layout.addLayoutItem(info_label)

# Date Info
info_label = QgsLayoutItemLabel(layout)
info_label.setText(date_text)
info_label.setFont(QFont(fontfamily, info_font_size))
info_label.setHAlign(Qt.AlignLeft)
info_label.attemptMove(QgsLayoutPoint(info_pos_x, date_pos_y, QgsUnitTypes.LayoutMillimeters))
info_label.adjustSizeToText()
layout.addLayoutItem(info_label)

# CRS Info
info_label = QgsLayoutItemLabel(layout)
info_label.setText(crs_text)
info_label.setFont(QFont(fontfamily, info_font_size))
info_label.setHAlign(Qt.AlignLeft)
info_label.attemptMove(QgsLayoutPoint(info_pos_x, crs_pos_y, QgsUnitTypes.LayoutMillimeters))
info_label.adjustSizeToText()
layout.addLayoutItem(info_label)

# Export Map
exporter = QgsLayoutExporter(layout)
if os.path.exists(EXPORT_PATH):
    os.remove(EXPORT_PATH)
export_result = exporter.exportToImage(EXPORT_PATH, QgsLayoutExporter.ImageExportSettings())
if export_result != QgsLayoutExporter.Success:
    print(f"Failed to export {LAYER_NAME} map!")
else:
    print(f"Map exported to: {EXPORT_PATH}")

# Cleanup QGIS
qgs.exitQgis()
