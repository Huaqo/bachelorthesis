from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean)
from qgis import processing

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class matplotlibHist(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    ATTRIBUTE = 'ATTRIBUTE'
    MAX_VALUE = 'MAX_VALUE'
    PLOT_OUTPUT = 'PLOT_OUTPUT'
    FIG_WIDTH = 'FIG_WIDTH'
    FIG_HEIGHT = 'FIG_HEIGHT'
    BINS = 'BINS'
    ALPHA = 'ALPHA'
    COLOR = 'COLOR'
    SHOW_GRID = 'SHOW_GRID'
    PLOT_TITLE = 'PLOT_TITLE'
    X_LABEL = 'X_LABEL'
    Y_LABEL = 'Y_LABEL'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return matplotlibHist()

    def name(self):
        return 'Histogram'

    def displayName(self):
        return self.tr('Histogram')

    def group(self):
        return self.tr('matplotlib vector')

    def groupId(self):
        return 'matplotlib vector'

    def shortHelpString(self):
        return self.tr("Generates a histogram plot for a selected numeric attribute from an input layer.")

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,self.tr('Input layer'),[QgsProcessing.TypeVectorAnyGeometry]))
        self.addParameter(QgsProcessingParameterField(self.ATTRIBUTE,self.tr('Attribute'),None,self.INPUT,QgsProcessingParameterField.Any))
        self.addParameter(QgsProcessingParameterNumber(self.MAX_VALUE, self.tr('Maximum Value'), QgsProcessingParameterNumber.Double, None, optional=True))
        self.addParameter(QgsProcessingParameterFileDestination('PLOT_OUTPUT',self.tr('Plot Output File'),'PNG Files (*.png)'))
        self.addParameter(QgsProcessingParameterNumber(self.FIG_WIDTH,self.tr('Figure Width'), QgsProcessingParameterNumber.Double, 10))
        self.addParameter(QgsProcessingParameterNumber(self.FIG_HEIGHT,self.tr('Figure Height'), QgsProcessingParameterNumber.Double, 6))
        self.addParameter(QgsProcessingParameterNumber(self.BINS, self.tr('Number of Bins'), QgsProcessingParameterNumber.Integer, 30 ))
        self.addParameter(QgsProcessingParameterNumber(self.ALPHA,self.tr('Alpha Transparency'), QgsProcessingParameterNumber.Double, 0.7))
        self.addParameter(QgsProcessingParameterString(self.COLOR,self.tr('Color'), defaultValue='blue'))
        self.addParameter(QgsProcessingParameterBoolean(self.SHOW_GRID,self.tr('Show Grid'), defaultValue=True))
        self.addParameter(QgsProcessingParameterString(self.PLOT_TITLE, self.tr('Plot Title'), defaultValue=' '))
        self.addParameter(QgsProcessingParameterString(self.X_LABEL, self.tr('X-axis Label'), defaultValue=' '))
        self.addParameter(QgsProcessingParameterString(self.Y_LABEL, self.tr('Y-axis Label'), defaultValue='Frequency'))

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        
        attribute_name = self.parameterAsString(parameters, self.ATTRIBUTE, context)
        
        attribute_values = []
        
        max_value = self.parameterAsDouble(parameters, self.MAX_VALUE, context) if parameters[self.MAX_VALUE] is not None else max(attribute_values)
        plot_output_path = self.parameterAsFileOutput(parameters, 'PLOT_OUTPUT', context)
        fig_width = self.parameterAsDouble(parameters, self.FIG_WIDTH, context)
        fig_height = self.parameterAsDouble(parameters, self.FIG_HEIGHT, context)
        bins = self.parameterAsInt(parameters, self.BINS, context)
        alpha = self.parameterAsDouble(parameters, self.ALPHA, context)
        color = self.parameterAsString(parameters, self.COLOR, context)
        show_grid = self.parameterAsBool(parameters, self.SHOW_GRID, context)
        plot_title = self.parameterAsString(parameters, self.PLOT_TITLE, context)
        x_label = self.parameterAsString(parameters, self.X_LABEL, context)
        y_label = self.parameterAsString(parameters, self.Y_LABEL, context)
            
        for feature in source.getFeatures():
            attribute_value = feature[attribute_name]
            if attribute_value is not None:
                attribute_values.append(attribute_value)

        if not attribute_values:
            raise QgsProcessingException(self.tr("No attribute values found. Please check the selected attribute."))
        
        try:
            plt.figure(figsize=(fig_width,fig_height))
            plt.hist(attribute_values, bins=bins,alpha=alpha, color=color, range=(min(attribute_values), max_value))
            plt.title(plot_title if plot_title else 'Value Distribution by Category')
            plt.xlabel(x_label if x_label else ' ')
            plt.ylabel(y_label if y_label else 'Frequence')
            if show_grid:
                plt.grid(True)
            else:
                plt.grid(False)
            plt.savefig(plot_output_path)
            plt.close()
            return {}
        except Exception as e:
            feedback.reportError(str(e))
            return {}