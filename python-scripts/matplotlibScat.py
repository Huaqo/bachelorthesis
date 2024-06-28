from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

class matplotlibScat(QgsProcessingAlgorithm):
    
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    X_VALUES = 'X_VALUES'
    Y_VALUES = 'Y_VALUES'
    X_MAX = 'X_MAX'
    Y_MAX = 'Y_MAX'
    FLIP_X = 'FLIP_X'
    FLIP_Y = 'FLIP_Y'
    COLOR = 'COLOR'
    TITLE = 'TITLE'
    X_LABEL = 'X_LABEL'
    Y_LABEL = 'Y_LABEL'


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return matplotlibScat()

    def name(self):
        return 'Scatter Plot'

    def displayName(self):
        return self.tr('Scatter Plot')

    def group(self):
        return self.tr('matplotlib vector')

    def groupId(self):
        return 'matplotlib vector'

    def shortHelpString(self):
        return self.tr("Generates a scatter plot for two selected numeric attributes from an input layer.")

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(QgsProcessingParameterFileDestination(
            'OUTPUT',
            self.tr('Plot Output File'),
            'PNG Files (*.png)'
        )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.X_VALUES,
                self.tr('X Values'),
                None,
                self.INPUT,
                QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Y_VALUES,
                self.tr('Y Values'),
                None,
                self.INPUT,
                QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.X_MAX,
                self.tr('X Max'),
                type=QgsProcessingParameterNumber.Double,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.Y_MAX,
                self.tr('Y Max'),
                type=QgsProcessingParameterNumber.Double,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.FLIP_X,
                self.tr('Flip X Axis'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.FLIP_Y,
                self.tr('Flip Y Axis'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.COLOR,
                self.tr('Color'),
                defaultValue='blue'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.TITLE,
                self.tr('Title'),
                defaultValue=' '
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.X_LABEL,
                self.tr('X Label'),
                defaultValue=' '
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.Y_LABEL,
                self.tr('Y Label'),
                defaultValue=' '
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        
        source = self.parameterAsSource(parameters, self.INPUT, context)
        x_field = self.parameterAsString(parameters, self.X_VALUES, context)
        y_field = self.parameterAsString(parameters, self.Y_VALUES, context)
        x_max = self.parameterAsDouble(parameters, self.X_MAX, context)
        y_max = self.parameterAsDouble(parameters, self.Y_MAX, context)
        flip_x = self.parameterAsBool(parameters, self.FLIP_X, context)
        flip_y = self.parameterAsBool(parameters, self.FLIP_Y, context)
        color = self.parameterAsString(parameters, self.COLOR, context)
        title = self.parameterAsString(parameters, self.TITLE, context)
        x_label = self.parameterAsString(parameters, self.X_LABEL, context)
        y_label = self.parameterAsString(parameters, self.Y_LABEL, context)
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        
        feedback.pushInfo(f"Source: {source}")
        feedback.pushInfo(f"x_field: {x_field}")
        feedback.pushInfo(f"y_field: {y_field}")
        feedback.pushInfo(f"x_max: {x_max}")
        feedback.pushInfo(f"y_max: {y_max}")
        feedback.pushInfo(f"flip_x: {flip_x}")
        feedback.pushInfo(f"flip_y: {flip_y}")
        feedback.pushInfo(f"title: {title}")
        feedback.pushInfo(f"x_label: {x_label}")
        feedback.pushInfo(f"y_label: {y_label}")
        feedback.pushInfo(f"output: {output}")

        x_values = []
        y_values = []

        for feature in source.getFeatures():
            try:
                x = float(feature[x_field])
                y = float(feature[y_field])
                if not (math.isnan(x) or math.isnan(y)):
                    x_values.append(x)
                    y_values.append(y)
            except Exception as e:
                continue

        feedback.pushInfo(f"x_values: {x_values}")
        feedback.pushInfo(f"y_values: {y_values}")
        
        try:
            plt.scatter(x_values, y_values, color=color)
            plt.xlim(0, x_max)
            plt.ylim(0, y_max)
            if flip_x:
                plt.gca().invert_xaxis()
            if flip_y:
                plt.gca().invert_yaxis()
            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.savefig(output)
            plt.close()
            feedback.pushInfo(f"Scatter plot saved to {output}")    
            return {self.OUTPUT: output}
        except Exception as e:  
            feedback.reportError(f"Error: {e}")
            return {}