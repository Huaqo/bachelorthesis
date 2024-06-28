import math
import matplotlib.pyplot as plt
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean)

import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')


class matplotlibExp(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    X_VALUES = 'X_VALUES'
    Y_VALUES = 'Y_VALUES'
    X_MAX = 'X_MAX'
    Y_MAX = 'Y_MAX'
    B = 'B'
    COLOR = 'COLOR'
    TITLE = 'TITLE'
    X_LABEL = 'X_LABEL'
    Y_LABEL = 'Y_LABEL'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return matplotlibExp()

    def name(self):
        return 'Exponential fit'

    def displayName(self):
        return self.tr('Exponential fit')

    def group(self):
        return self.tr('matplotlib vector')

    def groupId(self):
        return 'matplotlib vector'

    def shortHelpString(self):
        return self.tr("Generates a exponential fit for two selected numeric attributes from an input layer.")

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
            QgsProcessingParameterNumber(
                self.B,
                self.tr('b'),
                type = QgsProcessingParameterNumber.Double,
                optional=True
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
    
    @staticmethod
    def exponential_decay(x, a, b, c):
        return a * np.exp(b * x) + c
        
    @staticmethod
    def exponential_decay_no_offset(x,a,b):
        return a * np.exp(b * x)

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(parameters, self.INPUT, context)
        x_field = self.parameterAsString(parameters, self.X_VALUES, context)
        y_field = self.parameterAsString(parameters, self.Y_VALUES, context)
        x_max = self.parameterAsDouble(parameters, self.X_MAX, context)
        y_max = self.parameterAsDouble(parameters, self.Y_MAX, context)
        b = self.parameterAsDouble(parameters, self.B, context)
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

        grouped_data = {}

        for x, y in zip(x_values, y_values):
            if x not in grouped_data:
                grouped_data[x] = [y]
            else:
                grouped_data[x].append(y)

        max_y_values = {x: max(y_list) for x, y_list in grouped_data.items()}

        x_values_np = np.array(sorted(max_y_values.keys()))
        y_values_np = np.array([max_y_values[x] for x in x_values_np])
        
        positive_filter = y_values_np > 0
        
        x_values_positive = x_values_np[positive_filter]
        y_values_positive = y_values_np[positive_filter]
        
        if np.any(y_values_positive.min() <= 0):
            feedback.reportError("Negative values in y field")
            return {}
        
        initial_guess = [np.max(y_values_positive), b] # Assuming a starts at the max values, b is negative, c is zero
        
        try:
            popt, pcov = curve_fit(
                matplotlibExp.exponential_decay_no_offset, 
                x_values_positive, 
                y_values_positive,
                p0=initial_guess,
            )
            a_fit, b_fit = popt
            x_axis = np.linspace(x_values_positive.min(), x_values_positive.max(),500)
            y_fit = matplotlibExp.exponential_decay_no_offset(x_axis, a_fit, b_fit)

            feedback.pushInfo(f"Inital guess: {initial_guess}")
            feedback.pushInfo(f"Fit parameters: {popt}")


        except RuntimeError as e:
            feedback.reportError(f"Error during curve fitting: {e}")
            return{}
        
        try:
            plt.scatter(x_values_positive, y_values_positive)
            plt.plot(x_axis, y_fit, color=color, label='Fit Line')
            plt.xlim(x_values_positive.min(), x_max if x_max is not None else x_values_positive.max())
            plt.ylim(y_values_positive.min(), y_max if y_max is not None else y_values_positive.max())
            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.legend()
            plt.savefig(output)
            plt.close()
            feedback.pushInfo(f"Scatter plot saved to {output}")
            return {self.OUTPUT: output}
        except Exception as e:
            feedback.reportError(f"Error: {e}")
            return {}
